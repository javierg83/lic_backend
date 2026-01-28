from uuid import UUID
from psycopg2.extras import RealDictCursor
from src.core.database import Database
from src.core.responses import ApiResponse
from .schemas import DatosEconomicosShowResponse

class DatosEconomicosShowService:
    @staticmethod
    async def process(licitacion_id: UUID) -> ApiResponse[DatosEconomicosShowResponse]:
        conn = Database.get_connection()
        try:
            with conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(
                        """
                        SELECT id, licitacion_id, presupuesto_referencial, moneda, forma_pago, plazo_pago, fuente_financiamiento, observaciones
                        FROM finanzas_licitacion
                        WHERE licitacion_id = %s
                        """,
                        (str(licitacion_id),)
                    )
                    row = cur.fetchone()
                    
                    if not row:
                        return ApiResponse.fail(
                            message="Datos económicos no encontrados para esta licitación"
                        )
                    
                    datos = DatosEconomicosShowResponse(
                        id=row['id'],
                        licitacion_id=row['licitacion_id'],
                        presupuesto_referencial=row['presupuesto_referencial'],
                        moneda=row['moneda'],
                        forma_pago=row['forma_pago'],
                        plazo_pago=row['plazo_pago'],
                        fuente_financiamiento=row['fuente_financiamiento'],
                        observaciones=row['observaciones']
                    )
            
            return ApiResponse.ok(
                data=datos,
                message="Datos económicos obtenidos exitosamente"
            )

        except Exception as e:
            print(f"ERROR DatosEconomicosShowService: {str(e)}")
            return ApiResponse.fail(
                message="No se pudieron cargar los detalles financieros.",
                error=str(e)
            )
        finally:
            conn.close()
