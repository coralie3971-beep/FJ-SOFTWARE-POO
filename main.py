#Curso Programacion I
#Codigo 213023A_17
#Nombre Diana Milena Guerrero
#Unad 2026


# FJ-SOFTWARE-POO
Sistema Integral de Gestión de Clientes, Servicios y Reservas
from abc import ABC, abstractmethod
from datetime import datetime

# =======================================================
# 1. EXCEPCIONES PERSONALIZADAS EN CLIENTE, SERVICIO Y RESERVA
# =======================================================
class ClienteInvalidoError(Exception):
    """Excepción para errores en los datos del cliente."""
    pass

class ServicioInvalidoError(Exception):
    """Excepción para errores en la configuración de servicios."""
    pass

class ReservaError(Exception):
    """Excepción para operaciones no permitidas en reservas."""
    pass


# =======================================================
# 2. SISTEMA DE LOGS EN ARCHIVO
# =======================================================
class GestorBitacora:
    RUTA_LOG = "log_sistema.txt"

    @classmethod
    def registrar_evento(cls, nivel, mensaje):
        """Escribe los eventos y errores en un archivo de texto."""
        try:
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            linea = f"[{fecha_actual}] [{nivel.upper()}] - {mensaje}\n"
            with open(cls.RUTA_LOG, "a", encoding="utf-8") as archivo:
                archivo.write(linea)
        except Exception as error:
            print(f"Error al escribir en la bitácora de eventos: {error}")


# =======================================================
# 3. CLASES ABSTRACTAS Y CLASES DE DOMINIO
# =======================================================

class EntidadBase(ABC):
    """Clase abstracta base para entidades generales con ID y fecha."""
    def __init__(self, identificador):
        self.identificador = identificador
        self.fecha_registro = datetime.now()


class Cliente(EntidadBase):
    """Clase Cliente con encapsulación de datos y validaciones."""
    def __init__(self, identificador, documento, nombre, correo):
        super().__init__(identificador)
        self.documento = documento
        self.nombre = nombre
        self.correo = correo

    @property
    def documento(self):
        return self._documento

    @documento.setter
    def documento(self, valor):
        if not valor or len(str(valor).strip()) < 5:
            raise ClienteInvalidoError("El documento de identidad debe tener al menos 5 dígitos.")
        self._documento = str(valor).strip()

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        if not valor or not str(valor).strip():
            raise ClienteInvalidoError("El nombre del cliente no puede estar vacío.")
        self._nombre = str(valor).strip()

    @property
    def correo(self):
        return self._correo

    @correo.setter
    def correo(self, valor):
        if not valor or "@" not in str(valor):
            raise ClienteInvalidoError("El correo electrónico no es válido.")
        self._correo = str(valor).strip()


class Servicio(EntidadBase):
    """Clase abstracta base para los servicios de Software FJ."""
    def __init__(self, identificador, nombre_servicio, tarifa_base):
        super().__init__(identificador)
        self.nombre_servicio = nombre_servicio
        self.tarifa_base = tarifa_base

    @abstractmethod
    def calcular_costo_base(self, horas):
        pass

    @abstractmethod
    def obtener_descripcion(self):
        pass

    @abstractmethod
    def validar_parametros(self):
        pass

    # Métodos con parámetros opcionales (sobrecarga de cálculo de costos)
    def calcular_costo_total(self, horas, descuento=0.0, impuesto=0.0):
        costo = self.calcular_costo_base(horas)
        if descuento > 0:
            costo -= costo * (descuento / 100)
        if impuesto > 0:
            costo += costo * (impuesto / 100)
        return costo


class ReservaSala(Servicio):
    def __init__(self, identificador, nombre_servicio, tarifa_base, capacidad_personas):
        self.capacidad_personas = capacidad_personas
        super().__init__(identificador, nombre_servicio, tarifa_base)
        self.validar_parametros()

    def validar_parametros(self):
        if self.capacidad_personas <= 0:
            raise ServicioInvalidoError("La capacidad de la sala debe ser mayor a 0 personas.")
        if self.tarifa_base <= 0:
            raise ServicioInvalidoError("La tarifa base debe ser un número positivo.")

    def calcular_costo_base(self, horas):
        return self.tarifa_base * horas

    def obtener_descripcion(self):
        return f"Reserva de Sala: {self.nombre_servicio} (Capacidad: {self.capacidad_personas} personas)"


class AlquilerEquipo(Servicio):
    def __init__(self, identificador, nombre_servicio, tarifa_base, tipo_equipo):
        self.tipo_equipo = tipo_equipo
        super().__init__(identificador, nombre_servicio, tarifa_base)
        self.validar_parametros()

    def validar_parametros(self):
        if not self.tipo_equipo or not str(self.tipo_equipo).strip():
            raise ServicioInvalidoError("El tipo de equipo no puede estar vacío.")

    def calcular_costo_base(self, horas):
        seguro_fijo = 15000.0  # Seguro de mantenimiento del equipo
        return (self.tarifa_base * horas) + seguro_fijo

    def obtener_descripcion(self):
        return f"Alquiler de Equipo: {self.nombre_servicio} ({self.tipo_equipo})"


class AsesoriaEspecializada(Servicio):
    def __init__(self, identificador, nombre_servicio, tarifa_base, especialista):
        self.especialista = especialista
        super().__init__(identificador, nombre_servicio, tarifa_base)
        self.validar_parametros()

    def validar_parametros(self):
        if not self.especialista or not str(self.especialista).strip():
            raise ServicioInvalidoError("Debe asignar un especialista para el servicio.")

    def calcular_costo_base(self, horas):
        recargo_profesional = 1.20  # 20% adicional por honorarios
        return self.tarifa_base * horas * recargo_profesional

    def obtener_descripcion(self):
        return f"Asesoría Especializada: {self.nombre_servicio} con el Ing. {self.especialista}"


class Reserva(EntidadBase):
    def __init__(self, identificador, cliente, servicio, duracion_horas):
        super().__init__(identificador)
        if not cliente:
            raise ReservaError("No se puede crear una reserva sin cliente.")
        if not servicio:
            raise ReservaError("No se puede crear una reserva sin servicio.")
        if duracion_horas <= 0:
            raise ReservaError("La duración de la reserva debe ser de mínimo 1 hora.")

        self.cliente = cliente
        self.servicio = servicio
        self.duracion_horas = duracion_horas
        self.estado = "Pendiente"

    def confirmar_reserva(self):
        self.estado = "Confirmada"
        GestorBitacora.registrar_evento("INFO", f"Reserva #{self.identificador} confirmada para {self.cliente.nombre}.")

    def cancelar_reserva(self):
        self.estado = "Cancelada"
        GestorBitacora.registrar_evento("INFO", f"Reserva #{self.identificador} cancelada.")

    def procesar_pago(self, descuento=0, impuesto=0):
        if self.estado == "Cancelada":
            raise ReservaError(f"No se puede cobrar la reserva #{self.identificador} porque está cancelada.")
        
        total = self.servicio.calcular_costo_total(self.duracion_horas, descuento, impuesto)
        self.estado = "Procesada"
        GestorBitacora.registrar_evento("INFO", f"Pago procesado para Reserva #{self.identificador}. Total: ${total:,.2f} COP")
        return total


# =======================================================
# 4. SIMULACIÓN PARA LAS 10 OPERACIONES (EXCEPCIONES)
# =======================================================

def ejecutar_operacion(titulo, funcion):
    print(f"\n--- {titulo} ---")
    try:
        funcion()
    except (ClienteInvalidoError, ServicioInvalidoError, ReservaError) as error:
        print(f"  [EXCEPCIÓN CONTROLADA] {error}")
        GestorBitacora.registrar_evento("ERROR", str(error))
    except Exception as error_inesperado:
        print(f"  [ERROR GENERAL] {error_inesperado}")
        GestorBitacora.registrar_evento("CRITICAL", str(error_inesperado))
    else:
        # Se ejecuta solo si NO hubo error (cumple con try/except/else de la guía)
        print("  [OPERACIÓN FINALIZADA CON ÉXITO]")
    finally:
        # Se ejecuta SIEMPRE (cumple con try/except/finally de la guía)
        pass


def main():
    print("==================================================")
    print("    SISTEMA INTEGRAL DE GESTIÓN - FJ SOFTWARE   ")
    print("==================================================\n")

    GestorBitacora.registrar_evento("INFO", "Inicio de la simulación del programa.")

    clientes = []
    servicios = []
    reservas = []

    # Operación 1: Registro correcto de cliente
    def op1():
        c1 = Cliente(1, "1012345678", "Milena Guerrero", "coralie3971@email.com")
        clientes.append(c1)
        GestorBitacora.registrar_evento("INFO", f"Cliente creado: {c1.nombre}")
        print(f"  Cliente registrado: {c1.nombre}")
    ejecutar_operacion("Op 1: Registro de Cliente Válido", op1)

    # Operación 2: Intento con correo inválido
    def op2():
        c2 = Cliente(2, "987654321", "Juanita Silva", "juanitasilva.com")
        clientes.append(c2)
    ejecutar_operacion("Op 2: Registro de Cliente con Correo Inválido", op2)

    # Operación 3: Intento con documento corto
    def op3():
        c3 = Cliente(3, "123", "mabel Rozo", "mabel15@email.com")
        clientes.append(c3)
    ejecutar_operacion("Op 3: Registro de Cliente con Documento Inválido", op3)

    # Operación 4: Creación de servicio válido (Sala)
    def op4():
        s1 = ReservaSala(101, "Sala VIP A", 40000, 15)
        servicios.append(s1)
        GestorBitacora.registrar_evento("INFO", f"Servicio creado: {s1.nombre_servicio}")
        print(f"  Servicio registrado: {s1.obtener_descripcion()}")
    ejecutar_operacion("Op 4: Creación de Servicio Válido (Sala)", op4)

    # Operación 5: Creación de sala con capacidad 0 (Inválido)
    def op5():
        s2 = ReservaSala(102, "Sala Pequeña", 20000, 0)
        servicios.append(s2)
    ejecutar_operacion("Op 5: Creación de Sala con Capacidad 0 (Inválido)", op5)

    # Operación 6: Creación de equipo audiovisual
    def op6():
        s3 = AlquilerEquipo(103, "Proyector Laser 4K", 35000, "Audiovisual")
        servicios.append(s3)
        GestorBitacora.registrar_evento("INFO", f"Servicio creado: {s3.nombre_servicio}")
        print(f"  Servicio registrado: {s3.obtener_descripcion()}")
    ejecutar_operacion("Op 6: Creación de Servicio Válido (Alquiler Equipo)", op6)

    # Operación 7: Reserva válida y cobro
    def op7():
        r1 = Reserva(1001, clientes[0], servicios[0], 3)
        r1.confirmar_reserva()
        total = r1.procesar_pago(descuento=10, impuesto=19)
        reservas.append(r1)
        print(f"  Reserva #{r1.identificador} cobrada. Total: ${total:,.2f} COP")
    ejecutar_operacion("Op 7: Creación y Cobro de Reserva Válida", op7)

    # Operación 8: Reserva fallida (Duración 0 horas)
    def op8():
        r2 = Reserva(1002, clientes[0], servicios[0], 0)
    ejecutar_operacion("Op 8: Intentar Reserva con Duración de 0 horas", op8)

    # Operación 9: Creación de asesoría y cobro
    def op9():
        s4 = AsesoriaEspecializada(104, "Asesoría en Python", 80000, "Ramírez")
        servicios.append(s4)
        r3 = Reserva(1003, clientes[0], s4, 2)
        r3.confirmar_reserva()
        total = r3.procesar_pago()
        reservas.append(r3)
        print(f"  Reserva #{r3.identificador} procesada en {s4.nombre_servicio}. Total: ${total:,.2f} COP")
    ejecutar_operacion("Op 9: Creación de Asesoría y Procesamiento de Reserva", op9)

    # Operación 10: Intento de pago de reserva cancelada
    def op10():
        r4 = Reserva(1004, clientes[0], servicios[0], 2)
        r4.cancelar_reserva()
        r4.procesar_pago()
    ejecutar_operacion("Op 10: Intentar procesar pago de una Reserva Cancelada", op10)

    print("\n==================================================")
    print("   SIMULACIÓN FINALIZADA SIN CAÍDAS DEL SISTEMA   ")
    print("==================================================")
    print("Se ha generado el archivo 'log_sistema.txt' con todos los registros.")


if __name__ == "__main__":
    main()
