from psycopg2.extras import RealDictCursor
from src.core.database import Database
from src.core.responses import ApiResponse
from .schemas import DatosEconomicosUpdate, DatosEconomicosUpdateResponse

class DatosEconomicosUpdateService:
    @staticmethod
    async def process(licitacion_id: str, data: DatosEconomicosUpdate) -> ApiResponse[DatosEconomicosUpdateResponse]:
        conn = Database.get_connection()
        try:
            with conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # Check if entry exists for this licitacion
                    cur.execute("SELECT id FROM finanzas_licitacion WHERE licitacion_id = %s", (licitacion_id,))
                    row = cur.fetchone()
                    
                    if not row:
                        return ApiResponse.fail(message="Datos económicos no encontrados para esta licitación")
                    
                    record_id = row['id']
                    
                    # Build update query
                    fields_to_update = []
                    params = []
                    
                    update_data = data.model_dump(exclude_unset=True)
                    if not update_data:
                        return ApiResponse.fail(message="No se proporcionaron datos para actualizar")
                    
                    for key, value in update_data.items():
                        fields_to_update.append(f"{key} = %s")
                        params.append(value)
                    
                    params.append(record_id)
                    query = f"""
                        UPDATE finanzas_licitacion 
                        SET {', '.join(fields_to_update)} 
                        WHERE id = %s 
                        RETURNING id, licitacion_id, presupuesto_referencial, moneda, forma_pago, plazo_pago, fuente_financiamiento, observaciones
                    """
                    
                    cur.execute(query, tuple(params))
                    updated_row = cur.fetchone()
                    
                    if not updated_row:
                         return ApiResponse.fail(message="Error al actualizar los datos")

                    response_data = DatosEconomicosUpdateResponse(
                        id=str(updated_row['id']),
                        licitacion_id=str(updated_row['licitacion_id']),
                        presupuesto_referencial=updated_row['presupuesto_referencial'],
                        moneda=updated_row['moneda'],
                        forma_pago=updated_row['forma_pago'],
                        plazo_pago=updated_row['plazo_pago'],
                        fuente_financiamiento=updated_row['fuente_financiamiento'],
                        observaciones=updated_row['observaciones']
                    )
                    
                    return ApiResponse.ok(
                        data=response_data,
                        message="Datos económicos actualizados exitosamente"
                    )
        except Exception as e:
            print(f"ERROR DatosEconomicosUpdateService: {str(e)}")
            return ApiResponse.fail(
                message="No se pudieron guardar los cambios económicos. Verifique la conexión.",
                error=str(e)
            )
        finally:
            conn.close()
