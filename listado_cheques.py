from datetime import datetime
import csv
# https://pynative.com/python-timestamp/#h-what-is-timestamp-in-python 

headerF = ['DNI', 'Nro. de cheque', 'Tipo', 'Valor', 'Cuenta Origen', 'Cuenta Destino', 'Estado', 'Banco', 'Sucursal', 'Fecha de origen', 'Fecha de pago']

# Menú principal.
def main():
    print("""
    LISTADO DE CHEQUES
    ================================
    1. Consultar cheques
    2. Salir
    """)
    opt = validateInputNumber('Seleccione una opción: ')
    if opt == 1:
        ingresarParametros()
    else:
        return

# Maneja el ingreso de los parámetros y los envía a consultar().
def ingresarParametros():
    print("""
    CONSULTAR CHEQUES
    ================================
    """)
    archivo = input('Nombre del archivo a revisar (sin extensión): ').strip() + '.csv'
    dni = str(validateInputNumber('DNI del cliente: '))
    print("""
    Salida:
    1. PANTALLA
    2. CSV
    """)
    opt = validateInputNumber('Seleccione una salida: ')
    salida = 'PANTALLA' if opt == 1 else 'CSV'
    print("""
    Tipo de cheque:
    0. Todos
    1. EMITIDO
    2. DEPOSITADO
    """)
    opt = validateInputNumber('Seleccione un tipo de cheque: ')
    if opt == 1: tipo = 'EMITIDO'
    elif opt == 2: tipo = 'DEPOSITADO'
    else: tipo = ''
    print("""
    Estado del cheque:
    0. Todos
    1. PENDIENTE
    2. APROBADO
    3. RECHAZADO
    """)
    opt = validateInputNumber('Seleccione un estado: ')
    if opt == 1: estado = 'PENDIENTE'
    elif opt == 2: estado = 'APROBADO'
    elif opt == 3: estado = 'RECHAZADO'
    else: estado = ''
    rango_fecha = validateTimestamps('(Presione Enter para omitir) Rango fecha de origen (dd-mm-aaaa:dd-mm-aaaa): ')
    parametros = {'archivo':archivo, 'dni':dni, 'salida':salida, 'tipo':tipo, 'estado':estado, 'rango':rango_fecha}
    consultar(parametros)

# Consulta el archivo especificado, recolecta los resultados y los envía a una función de salida.
def consultar(parametros):
    try:
        file = open(parametros['archivo'], 'r')
        csvreader = csv.reader(file)
        cheques = []
        header = next(csvreader)
        filterTipo = True if parametros['tipo'] != '' else False
        filterEstado = True if parametros['estado'] != '' else False
        filterRango = True if parametros['rango'] != '' else False
        for row in csvreader:
            if parametros['dni'] == row[0]:
                cheques.append(row)
        repeated = searchRepeated(cheques)
        if repeated != None:
            print('='*60)
            print(f'ERROR: El cheque {repeated} se repite.')
            print('='*60)
        if filterTipo:
            cheques = filtrar(cheques, parametros['tipo'], 2)
        if filterEstado:
            cheques = filtrar(cheques, parametros['estado'], 6)
        if filterRango:
            cheques = filtrarFechas(cheques, parametros['rango'])
        if parametros['salida'] == 'PANTALLA':
            mostrarPantalla(cheques)
        else:
            cheques.insert(0, header)
            timestamp = datetime.now()
            filename = parametros['dni'] + '_' + formatStamp(str(timestamp))
            guardarCSV(filename, cheques)
    except FileNotFoundError:
        print(f'No se encuentra el archivo ' + parametros['archivo'])
    finally:
        file.close()
    return

# Filtra el batch para que la referencia (valor del parámetro indicado) coincida con el valor del item (pos) del cheque que corresponde a dicho parámetro.
# Esta implementación permite filtrar los cheques tanto por su tipo como por su estado.
def filtrar(cheques, referencia, pos):
    aux = []
    for cheque in cheques:
        if referencia == cheque[pos]:
            aux.append(cheque)
    return aux

# Filtra el batch para que las fechas (de origen) de cada cheque se encuentren dentro del rango.
def filtrarFechas(cheques, rango):
    dates = desarmarRango(rango)
    date_from = toDateTime(dates['date_from'])
    date_to = toDateTime(dates['date_to'])
    aux = []
    for cheque in cheques:
        dt_obj = toDateTime(cheque[9])
        if date_from <= dt_obj and dt_obj <= date_to:
            aux.append(cheque)
    return aux

# Muestra el resultado por consola.
def mostrarPantalla(cheques):
    print('SALIDA POR PANTALLA')
    print('-'*180)
    print(f'{headerF[0]:15}{headerF[1]:20}{headerF[2]:15}{headerF[3]:15}{headerF[4]:15}{headerF[5]:20}{headerF[6]:15}{headerF[7]:10}{headerF[8]:10}{headerF[9]:20}{headerF[10]:15}')
    for cheque in cheques:
        print(f'{cheque[0]:15}{cheque[1]:20}{cheque[2]:15}{cheque[3]:15}{cheque[4]:15}{cheque[5]:20}{cheque[6]:15}{cheque[7]:10}{cheque[8]:10}{cheque[9]:20}{cheque[10]:15}')
    print('-'*180)

# Exporta el resultado a un archivo CSV.
def guardarCSV(filename, cheques):
    print('EXPORTAR A CSV')
    file = open(filename + '.csv', 'w')
    for cheque in cheques:
        file.write(','.join(cheque) + '\n')
    file.close()
    print('='*100)
    print(f'Archivo {filename}.csv creado con éxito!')
    print('='*100)

# Formatea el timestamp de la siguiente forma: 'yyyy-mm-dd hh:mm:ss.cccccc' => 'yyyy-mm-dd_hh.mm.ss'.
def formatStamp(stamp):
    formatted = ''
    for chr in stamp:
        if chr == ' ':
            formatted += '_'
        elif chr == ':':
            formatted += '.'
        elif chr == '.':
            break
        else:
            formatted += chr
    return formatted

# Valida que el formato del rango de fechas sea el correcto.
def validateTimestamps(message):
    stamp = input(message)
    if stamp == '':
        return stamp
    try:
        dates = desarmarRango(stamp)
        date_from = toDateTime(dates['date_from'])
        date_to = toDateTime(dates['date_to'])
        return stamp
    except:
        print('Formato incorrecto')
        validateTimestamps(message)

# Extrae los extremos del rango de fechas: 'date_from:date_to'
def desarmarRango(rango):
    date_from = ''
    date_to = ''
    flag = False
    for char in rango:
        if char == ':':
            flag = True
            continue
        
        if not flag:
            date_from += char
        else:
            date_to += char
    return {'date_from':date_from, 'date_to':date_to}

# Convierte un string de fecha a formato datetime.
def toDateTime(date_str):
    format_str = '%d-%m-%Y'
    datetime_obj = datetime.strptime(date_str, format_str)
    return datetime_obj

# Busca cheques repetidos para un DNI. Si encuentra uno, lo devuelve.
def searchRepeated(cheques):
    numeros = []
    for cheque in cheques:
        numeros.append(cheque[1])
    for nro in numeros:
        if numeros.count(nro) > 1:
            return nro
    return None

# Obliga que el input pueda convertirse a número.
def validateInputNumber(message):
    while True:
        try:
            v = int(input(message))
            break
        except:
            print('Ingrese un valor numérico...')
    return v 

if __name__ == '__main__':
    main()
    