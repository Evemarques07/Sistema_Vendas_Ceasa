from typing import List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from decimal import Decimal
from datetime import datetime

from app.models.estoque import EstoqueFifo, MovimentacaoCaixa, LucroBruto, EntradaEstoque, TipoMovimentacao
from app.models.venda import Venda, ItemVenda
from app.models.produto import Produto

class FluxoCaixaService:
    """Serviço para gerenciar fluxo de caixa com controle FIFO"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def registrar_entrada_estoque(self, entrada: EntradaEstoque) -> None:
        """Registra entrada de estoque no controle FIFO"""
        # Criar registro FIFO
        estoque_fifo = EstoqueFifo(
            produto_id=entrada.produto_id,
            entrada_estoque_id=entrada.id,
            quantidade_restante=entrada.quantidade,
            preco_custo_unitario=entrada.preco_custo,
            data_entrada=entrada.data_entrada,
            finalizado=False
        )
        self.db.add(estoque_fifo)
        
        # Registrar movimentação de caixa (entrada)
        movimentacao = MovimentacaoCaixa(
            produto_id=entrada.produto_id,
            entrada_estoque_id=entrada.id,
            tipo_movimentacao=TipoMovimentacao.ENTRADA,
            quantidade=entrada.quantidade,
            preco_unitario=entrada.preco_custo,
            valor_total=entrada.valor_total,
            observacoes=f"Entrada de estoque - {entrada.fornecedor or 'Não informado'}"
        )
        self.db.add(movimentacao)
        self.db.commit()
    
    def processar_venda_separada(self, venda: Venda) -> List[LucroBruto]:
        """Processa venda separada aplicando FIFO e calculando lucro bruto"""
        lucros = []
        
        for item in venda.itens:
            if item.quantidade_real and item.quantidade_real > 0:
                lucro = self._calcular_custo_fifo(venda, item)
                if lucro:
                    lucros.append(lucro)
        
        return lucros
    
    def _calcular_custo_fifo(self, venda: Venda, item: ItemVenda) -> LucroBruto:
        """Calcula custo usando método FIFO e gera registro de lucro bruto"""
        quantidade_pendente = item.quantidade_real
        custo_total = Decimal('0')
        
        # Buscar estoques FIFO não finalizados, ordenados por data de entrada (FIFO)
        estoques_fifo = self.db.query(EstoqueFifo).filter(
            and_(
                EstoqueFifo.produto_id == item.produto_id,
                EstoqueFifo.finalizado == False,
                EstoqueFifo.quantidade_restante > 0
            )
        ).order_by(EstoqueFifo.data_entrada).all()
        
        # Aplicar FIFO para calcular custo
        for estoque in estoques_fifo:
            if quantidade_pendente <= 0:
                break
            
            quantidade_usada = min(quantidade_pendente, estoque.quantidade_restante)
            custo_parcial = quantidade_usada * estoque.preco_custo_unitario
            custo_total += custo_parcial
            
            # Atualizar estoque FIFO
            estoque.quantidade_restante -= quantidade_usada
            if estoque.quantidade_restante <= 0:
                estoque.finalizado = True
            
            quantidade_pendente -= quantidade_usada
        
        if quantidade_pendente > 0:
            # Se ainda há quantidade pendente, usar custo médio dos últimos estoques
            ultimo_estoque = self.db.query(EstoqueFifo).filter(
                EstoqueFifo.produto_id == item.produto_id
            ).order_by(desc(EstoqueFifo.data_entrada)).first()
            
            if ultimo_estoque:
                custo_restante = quantidade_pendente * ultimo_estoque.preco_custo_unitario
                custo_total += custo_restante
        
        # Calcular receita total
        receita_total = item.quantidade_real * item.valor_unitario
        
        # Calcular lucro bruto
        lucro_bruto_valor = receita_total - custo_total
        margem_percentual = (lucro_bruto_valor / receita_total * 100) if receita_total > 0 else Decimal('0')
        
        # Criar registro de lucro bruto
        lucro_bruto = LucroBruto(
            venda_id=venda.id,
            produto_id=item.produto_id,
            quantidade_vendida=item.quantidade_real,
            custo_total=custo_total,
            receita_total=receita_total,
            lucro_bruto=lucro_bruto_valor,
            margem_percentual=margem_percentual
        )
        self.db.add(lucro_bruto)
        
        # Registrar movimentação de caixa (saída)
        movimentacao = MovimentacaoCaixa(
            produto_id=item.produto_id,
            venda_id=venda.id,
            tipo_movimentacao=TipoMovimentacao.SAIDA,
            quantidade=item.quantidade_real,
            preco_unitario=item.valor_unitario,
            valor_total=receita_total,
            observacoes=f"Venda #{venda.id} - Cliente: {venda.cliente.nome if venda.cliente else 'Balcão'}"
        )
        self.db.add(movimentacao)
        
        self.db.commit()
        return lucro_bruto
    
    def reverter_venda_cancelada(self, venda: Venda) -> None:
        """Reverte movimentações de uma venda cancelada"""
        # Buscar registros de lucro bruto da venda
        lucros = self.db.query(LucroBruto).filter(LucroBruto.venda_id == venda.id).all()
        
        for lucro in lucros:
            # Restaurar quantidade nos estoques FIFO
            self._restaurar_estoque_fifo(lucro)
            
            # Remover movimentação de caixa de saída
            movimentacao_saida = self.db.query(MovimentacaoCaixa).filter(
                and_(
                    MovimentacaoCaixa.venda_id == venda.id,
                    MovimentacaoCaixa.produto_id == lucro.produto_id,
                    MovimentacaoCaixa.tipo_movimentacao == TipoMovimentacao.SAIDA
                )
            ).first()
            if movimentacao_saida:
                self.db.delete(movimentacao_saida)
            
            # Remover registro de lucro bruto
            self.db.delete(lucro)
        
        self.db.commit()
    
    def _restaurar_estoque_fifo(self, lucro: LucroBruto) -> None:
        """Restaura quantidades no estoque FIFO quando uma venda é cancelada"""
        quantidade_restaurar = lucro.quantidade_vendida
        
        # Buscar estoques FIFO em ordem inversa (último usado primeiro)
        estoques_fifo = self.db.query(EstoqueFifo).filter(
            EstoqueFifo.produto_id == lucro.produto_id
        ).order_by(desc(EstoqueFifo.data_entrada)).all()
        
        for estoque in estoques_fifo:
            if quantidade_restaurar <= 0:
                break
            
            # Calcular quanto pode ser restaurado neste estoque
            entrada_original = self.db.query(EntradaEstoque).filter(
                EntradaEstoque.id == estoque.entrada_estoque_id
            ).first()
            
            if entrada_original:
                quantidade_maxima = entrada_original.quantidade
                quantidade_atual = estoque.quantidade_restante
                espaco_disponivel = quantidade_maxima - quantidade_atual
                
                quantidade_a_restaurar = min(quantidade_restaurar, espaco_disponivel)
                
                if quantidade_a_restaurar > 0:
                    estoque.quantidade_restante += quantidade_a_restaurar
                    estoque.finalizado = False
                    quantidade_restaurar -= quantidade_a_restaurar
    
    def obter_relatorio_fluxo_caixa(self, produto_id: int = None, 
                                   data_inicio: datetime = None, 
                                   data_fim: datetime = None) -> dict:
        """Gera relatório de fluxo de caixa"""
        query = self.db.query(MovimentacaoCaixa)
        
        if produto_id:
            query = query.filter(MovimentacaoCaixa.produto_id == produto_id)
        if data_inicio:
            query = query.filter(MovimentacaoCaixa.data_movimentacao >= data_inicio)
        if data_fim:
            query = query.filter(MovimentacaoCaixa.data_movimentacao <= data_fim)
        
        movimentacoes = query.order_by(MovimentacaoCaixa.data_movimentacao).all()
        
        total_entradas = sum(
            mov.valor_total for mov in movimentacoes 
            if mov.tipo_movimentacao == TipoMovimentacao.ENTRADA
        )
        
        total_saidas = sum(
            mov.valor_total for mov in movimentacoes 
            if mov.tipo_movimentacao == TipoMovimentacao.SAIDA
        )
        
        # Calcular lucro bruto
        query_lucro = self.db.query(LucroBruto)
        if produto_id:
            query_lucro = query_lucro.filter(LucroBruto.produto_id == produto_id)
        if data_inicio:
            query_lucro = query_lucro.filter(LucroBruto.data_calculo >= data_inicio)
        if data_fim:
            query_lucro = query_lucro.filter(LucroBruto.data_calculo <= data_fim)
        
        lucros = query_lucro.all()
        lucro_bruto_total = sum(lucro.lucro_bruto for lucro in lucros)
        margem_media = (
            sum(lucro.margem_percentual for lucro in lucros) / len(lucros)
            if lucros else Decimal('0')
        )
        
        return {
            "movimentacoes": movimentacoes,
            "total_entradas": total_entradas,
            "total_saidas": total_saidas,
            "saldo": total_saidas - total_entradas,  # Receita - Custo
            "lucro_bruto_total": lucro_bruto_total,
            "margem_media": margem_media,
            "quantidade_vendas": len([m for m in movimentacoes if m.tipo_movimentacao == TipoMovimentacao.SAIDA])
        }
