# BambuLuc v1.3.0 🖨️

**Control completo para impresoras Bambu Lab via conexión de red**

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![PyPI Version](https://img.shields.io/pypi/v/bambuluc.svg)](https://pypi.org/project/bambuluc/)
[![License](https://img.shields.io/badge/license-Commercial-red.svg)](LICENSE)

## 🌟 Características

BambuLuc es una librería Python completa para controlar impresoras Bambu Lab de forma programática. Incluye todas las funciones necesarias para automatizar completamente el proceso de impresión 3D.

### ✅ **Control Manual Completo**
- 🏠 HOME de ejes (individual o todos)
- 🌡️ Control de temperaturas (nozzle y cama)
- 🎯 Movimientos precisos de ejes X/Y/Z
- 💧 Control de extrusión y retracción
- 💡 Control de LED de cámara
- 🌪️ Control de ventiladores

### ✅ **Sistema AMS (Automatic Material System)**
- 🔧 Configuración automática de slots
- 📋 Detección de filamentos requeridos
- 🔄 Cambio automático de materiales
- 🎨 Gestión de filamentos multicolor

### ✅ **Transferencia de Archivos**
- 📁 Subida de archivos .3mf/.gcode por FTP SSL
- 🚀 Proceso de subida optimizado y seguro
- 📤 Gestión automática de conexiones

### ✅ **Automatización Completa**
- ⚡ Proceso completo en una función
- 🎯 AMS automático + subida + impresión
- 📝 Envío de comandos personalizados

### ✅ **Monitoreo de Estados**
- 📊 Consulta de estado de impresión en tiempo real
- 🌡️ Monitoreo de temperaturas
- 📈 Progreso de impresión
- 🔍 Estados detallados de la máquina

## 🚀 Instalación

```bash
pip install bambuluc
```

## 📖 Uso Básico

### Configuración Inicial

```python
from bambuluc import BambuLuc

# Configuración de conexión
printer = BambuLuc(
    ip="IP_IMPRESORA",          # ej: 192.168.1.100
    access_code="CODIGO_ACCESO", # Código de acceso de la impresora
    serial="SERIE_IMPRESORA"     # Número de serie de la impresora
)
```

> **Nota:** Configura tu impresora con `IP_IMPRESORA`, `CODIGO_ACCESO` y `SERIE_IMPRESORA` con los valores reales de tu impresora Bambu Lab.

### Control Manual

```python
import asyncio

async def control_manual():
    printer = BambuLuc("IP_IMPRESORA", "CODIGO_ACCESO", "SERIE_IMPRESORA")
    
    try:
        # Conectar
        await printer.connect()
        
        # Hacer HOME de todos los ejes
        await printer.home_all()
        
        # Calentar nozzle a 210°C
        await printer.set_nozzle_temperature(210)
        
        # Calentar cama a 60°C
        await printer.set_bed_temperature(60)
        
        # Mover a posición
        await printer.move_x(100)
        await printer.move_y(100)
        await printer.move_z(50)
        
        # Extruir filamento
        await printer.extrude(10)
        
    finally:
        await printer.disconnect()

# Ejecutar
asyncio.run(control_manual())
```

### Configuración AMS y Subida de Archivo

```python
async def configurar_ams_y_subir():
    printer = BambuLuc("IP_IMPRESORA", "CODIGO_ACCESO", "SERIE_IMPRESORA")
    
    try:
        await printer.connect()
        
        # Configurar AMS (4 slots con diferentes filamentos)
        filamentos_requeridos = ["PLA", "PETG", "ABS", "TPU"]
        await printer.configure_ams(filamentos_requeridos)
        
        # Subir archivo 3MF por FTP
        resultado = await printer.upload_file("mi_modelo.3mf")
        if resultado:
            print("✅ Archivo subido exitosamente")
        else:
            print("❌ Error al subir archivo")
            
    finally:
        await printer.disconnect()

asyncio.run(configurar_ams_y_subir())
```

### 📊 Consulta de Estados

```python
async def consultar_estados():
    printer = BambuLuc("IP_IMPRESORA", "CODIGO_ACCESO", "SERIE_IMPRESORA")
    
    try:
        await printer.connect()
        
        # Estado general de impresión
        estado = await printer.get_print_status()
        print(f"Estado: {estado}")
        
        # Progreso de impresión (0-100%)
        progreso = await printer.get_print_progress()
        print(f"Progreso: {progreso}%")
        
        # Temperaturas actuales
        temp_nozzle = await printer.get_nozzle_temperature()
        temp_bed = await printer.get_bed_temperature()
        print(f"Nozzle: {temp_nozzle}°C, Cama: {temp_bed}°C")
        
        # Estado de la cama (nivelación, etc.)
        estado_cama = await printer.get_bed_status()
        print(f"Estado cama: {estado_cama}")
        
        # Información del filamento actual
        filamento_info = await printer.get_current_filament()
        print(f"Filamento: {filamento_info}")
        
    finally:
        await printer.disconnect()

asyncio.run(consultar_estados())
```

### Proceso Completo Automatizado

```python
async def proceso_completo():
    printer = BambuLuc("IP_IMPRESORA", "CODIGO_ACCESO", "SERIE_IMPRESORA")
    
    try:
        await printer.connect()
        
        # AMS + Subida + Impresión en un solo paso
        resultado = await printer.auto_print(
            archivo="modelo.3mf",
            filamentos_requeridos=["PLA", "PETG"]
        )
        
        if resultado:
            print("🎉 ¡Proceso completo exitoso!")
            
            # Monitorear progreso
            while True:
                estado = await printer.get_print_status()
                progreso = await printer.get_print_progress()
                
                print(f"Estado: {estado} - Progreso: {progreso}%")
                
                if estado in ["FINISH", "FAILED"]:
                    break
                    
                await asyncio.sleep(30)  # Revisar cada 30 segundos
        else:
            print("❌ Error en el proceso")
            
    finally:
        await printer.disconnect()

# Ejecutar proceso completo
if __name__ == "__main__":
    result = asyncio.run(proceso_completo())
```

## 🔧 Control Avanzado

### Movimientos Precisos

```python
async def movimientos_avanzados():
    printer = BambuLuc("IP_IMPRESORA", "CODIGO_ACCESO", "SERIE_IMPRESORA")
    
    try:
        await printer.connect()
        
        # Movimiento coordinado XYZ
        await printer.move_xyz(x=150, y=150, z=100)
        
        # Movimiento relativo
        await printer.move_relative(x=10, y=-5)
        
        # Control de velocidad de extrusión
        await printer.set_extrusion_rate(110)  # 110% velocidad
        
        # Retraer filamento
        await printer.retract(2)  # Retraer 2mm
        
    finally:
        await printer.disconnect()

asyncio.run(movimientos_avanzados())
```

### Control de Ventiladores y LED

```python
async def control_ventiladores():
    printer = BambuLuc("IP_IMPRESORA", "CODIGO_ACCESO", "SERIE_IMPRESORA")
    
    try:
        await printer.connect()
        
        # Encender ventilador de capa al 80%
        await printer.set_part_fan(80)
        
        # Ventilador auxiliar al 50%
        await printer.set_aux_fan(50)
        
        # Encender LED de cámara
        await printer.set_camera_led(True)
        
        # Apagar LED después de 10 segundos
        await asyncio.sleep(10)
        await printer.set_camera_led(False)
        
    finally:
        await printer.disconnect()

asyncio.run(control_ventiladores())
```

## 📋 Requisitos

- Python 3.7+
- Impresora Bambu Lab compatible (A1 mini, A1, X1C, P1P, P1S, etc.)
- Conexión de red con la impresora
- Código de acceso de la impresora habilitado

## ⚠️ Configuración Requerida

Antes de usar BambuLuc, configura tu impresora:

1. **Habilitar acceso LAN**: 
   - Menú impresora → Configuración → LAN → Habilitar
   
2. **Obtener código de acceso**:
   - Menú impresora → Configuración → LAN → Código de acceso
   
3. **Obtener número de serie**:
   - Menú impresora → Configuración → General → Información del dispositivo

### Parámetros de Configuración

- `IP_IMPRESORA`: Dirección IP de tu impresora (ej: 192.168.1.100)
- `CODIGO_ACCESO`: Código de 8 dígitos de acceso LAN 
- `SERIE_IMPRESORA`: Número de serie de 15 caracteres

## 🛠️ Métodos Disponibles

### Conexión
- `connect()` - Conectar a la impresora
- `disconnect()` - Desconectar de la impresora

### Control Manual
- `home_all()` - HOME todos los ejes
- `home_x()`, `home_y()`, `home_z()` - HOME ejes individuales
- `move_x(pos)`, `move_y(pos)`, `move_z(pos)` - Movimientos absolutos
- `move_xyz(x, y, z)` - Movimiento coordinado
- `move_relative(x, y)` - Movimiento relativo

### Temperaturas
- `set_nozzle_temperature(temp)` - Establecer temperatura nozzle
- `set_bed_temperature(temp)` - Establecer temperatura cama
- `get_nozzle_temperature()` - Obtener temperatura actual nozzle
- `get_bed_temperature()` - Obtener temperatura actual cama

### Extrusión
- `extrude(length)` - Extruir filamento
- `retract(length)` - Retraer filamento
- `set_extrusion_rate(rate)` - Velocidad de extrusión (%)

### Control de Ventiladores/LED
- `set_part_fan(speed)` - Ventilador de capa (0-100%)
- `set_aux_fan(speed)` - Ventilador auxiliar (0-100%)
- `set_camera_led(on)` - LED de cámara (True/False)

### Sistema AMS
- `configure_ams(filaments)` - Configurar slots AMS
- `get_current_filament()` - Información filamento actual

### Transferencia y Control
- `upload_file(filepath)` - Subir archivo por FTP
- `auto_print(archivo, filamentos)` - Proceso completo automatizado

### Estados y Monitoreo
- `get_print_status()` - Estado de impresión actual
- `get_print_progress()` - Progreso de impresión (%)
- `get_bed_status()` - Estado de la cama
- `get_machine_status()` - Estado general de la máquina

## 🐛 Solución de Problemas

### Error de Conexión
- Verificar que la impresora está encendida y conectada a la red
- Comprobar la IP de la impresora
- Verificar que el acceso LAN está habilitado

### Error de Autenticación
- Verificar el código de acceso de 8 dígitos
- Verificar el número de serie de 15 caracteres
- Regenerar código de acceso si es necesario

### Error de Subida FTP
- Verificar que el archivo existe
- Comprobar formato del archivo (.3mf o .gcode)
- Verificar espacio disponible en la impresora

## 🤝 Contribuir

1. Fork del repositorio
2. Crear rama para nueva característica
3. Commit de cambios
4. Push a la rama
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo una **Licencia Comercial Personalizada**:

- ✅ **GRATIS** para uso personal, educativo e investigación
- ❌ **USO COMERCIAL PROHIBIDO** sin licencia separada  
- 💰 **ROYALTIES** requeridos para uso comercial

Para **licencias comerciales**, contacta:
- GitHub: [AngelBarbero](https://github.com/AngelBarbero)
- Issues: [bambuluc/issues](https://github.com/AngelBarbero/bambuluc/issues) con etiqueta "Commercial License Request"

Ver `LICENSE` para términos completos.

## 🆘 Soporte

- **GitHub Issues**: [Reportar bugs](https://github.com/AngelBarbero/bambuluc/issues)
- **Documentación**: Este README
- **GitHub**: [AngelBarbero](https://github.com/AngelBarbero)

## 🏷️ Versiones

### v1.3.0 (Actual)
- ✅ Control manual completo
- ✅ Sistema AMS automático
- ✅ Transferencia FTP SSL
- ✅ Proceso automatizado completo
- ✅ Monitoreo de estados en tiempo real
- ✅ Control avanzado de ventiladores y LED

---

**Desarrollado con ❤️ por Angel Luis Barbero Guerras**

*¡Automatiza tu impresión 3D con BambuLuc!* 🚀
