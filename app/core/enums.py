"""
Enums centralizados para todo o sistema
"""
import enum

class TipoMedida(str, enum.Enum):
    """
    Tipos de medida padronizados para produtos e vendas
    """
    KG = "kg"                # Quilogramas
    UNIDADE = "unidade"      # Unidades
    LITRO = "litro"          # Litros
    CAIXA = "caixa"          # Caixas
    SACO = "saco"            # Sacos
    DUZIA = "duzia"          # Dúzias

class SituacaoPedido(str, enum.Enum):
    """
    Situações possíveis de um pedido/venda
    """
    A_SEPARAR = "A separar"
    SEPARADO = "Separado"

class SituacaoPagamento(str, enum.Enum):
    """
    Situações possíveis de pagamento
    """
    PAGO = "Pago"
    PENDENTE = "Pendente"

class TipoUsuario(str, enum.Enum):
    """
    Tipos de usuário do sistema
    """
    ADMINISTRADOR = "administrador"
    FUNCIONARIO = "funcionario"
