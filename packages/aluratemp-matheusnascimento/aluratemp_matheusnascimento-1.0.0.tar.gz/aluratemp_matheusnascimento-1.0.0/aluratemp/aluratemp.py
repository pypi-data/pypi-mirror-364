# Conversão de temperatura de Fahrenheit para Celsius

"""graus = input('Digite a temperatura em Fahrenheit: ')"""

def celsius_para_fahrenheit(temp_em_celsius):
    temp_em_fahrenheit = 1.8 * temp_em_celsius + 32
    return temp_em_fahrenheit
def fahrenheit_para_celsius(temp_em_fahrenheit):
    temp_em_celsius = (temp_em_fahrenheit - 32) / 1.8
    return temp_em_celsius

if __name__ == '__main__':
    print('{} ºC'.format(fahrenheit_para_celsius(int(50))))
    print('{} ºF'.format(celsius_para_fahrenheit(10)))