#!/usr/bin/env python3
"""
Script para procesar archivos CSV de mediciones de celdas solares
Genera 4 archivos CSV con métricas: Jsc, Voc, Fill Factor, Efficiency
"""

import csv
import sys
from pathlib import Path
from typing import List, Dict, Tuple


def parse_csv_file(filepath: str) -> List[Dict[str, any]]:
    """
    Parse un archivo CSV y extrae todos los experimentos con sus métricas.

    Returns:
        Lista de diccionarios, cada uno representa un experimento con sus métricas
    """
    experiments = []

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Buscar inicio de experimento (línea con "Filename,")
        if line.startswith('Filename,'):
            experiment = {}
            experiment['filename'] = line.split(',')[1].strip()

            # Siguiente línea: Comments/Coments
            i += 1
            if i < len(lines):
                comment_line = lines[i].strip()
                if comment_line.startswith('Comment') or comment_line.startswith('Coment'):
                    experiment['comment'] = comment_line.split(',')[1].strip() if ',' in comment_line else ''

            # Columnas de la curva I-V (se definen al encontrar "Voltage / V,")
            curve_cols = None

            # Buscar las métricas en las siguientes líneas
            i += 1
            while i < len(lines):
                metric_line = lines[i].strip()

                # Si encontramos otro experimento, retroceder y salir
                if metric_line.startswith('Filename,'):
                    i -= 1
                    break

                # Buscar métricas específicas
                if metric_line.startswith('Jsc / mA cm^-2,'):
                    parts = metric_line.split(',')
                    experiment['Jsc'] = {
                        'avg': parts[1].strip() if len(parts) > 1 else '',
                        'fs': parts[2].strip() if len(parts) > 2 else '',
                        'bs': parts[3].strip() if len(parts) > 3 else ''
                    }

                elif metric_line.startswith('Voc / V,'):
                    parts = metric_line.split(',')
                    experiment['Voc'] = {
                        'avg': parts[1].strip() if len(parts) > 1 else '',
                        'fs': parts[2].strip() if len(parts) > 2 else '',
                        'bs': parts[3].strip() if len(parts) > 3 else ''
                    }

                elif metric_line.startswith('Fill Factor,'):
                    parts = metric_line.split(',')
                    experiment['Fill Factor'] = {
                        'avg': parts[1].strip() if len(parts) > 1 else '',
                        'fs': parts[2].strip() if len(parts) > 2 else '',
                        'bs': parts[3].strip() if len(parts) > 3 else ''
                    }

                elif metric_line.startswith('Efficiency / %,'):
                    parts = metric_line.split(',')
                    experiment['Efficiency'] = {
                        'avg': parts[1].strip() if len(parts) > 1 else '',
                        'fs': parts[2].strip() if len(parts) > 2 else '',
                        'bs': parts[3].strip() if len(parts) > 3 else ''
                    }

                elif metric_line.startswith('Rs / ohm,'):
                    parts = metric_line.split(',')
                    experiment['Rs'] = {
                        'avg': parts[1].strip() if len(parts) > 1 else '',
                        'fs': parts[2].strip() if len(parts) > 2 else '',
                        'bs': parts[3].strip() if len(parts) > 3 else ''
                    }

                # Inicio de la curva I-V: ubicar las columnas por nombre
                elif metric_line.startswith('Voltage / V,'):
                    headers = [h.strip() for h in metric_line.split(',')]
                    if 'J1 / mA cm^-2' in headers and 'J2 / mA cm^-2' in headers:
                        curve_cols = (
                            headers.index('Voltage / V'),
                            headers.index('J1 / mA cm^-2'),
                            headers.index('J2 / mA cm^-2'),
                        )
                        experiment['curve'] = []
                    else:
                        print(f"  Warning: curva sin columnas J1/J2 en {filepath}")

                # Puntos de la curva I-V: una fila numérica por voltaje
                elif curve_cols and metric_line:
                    parts = [p.strip() for p in metric_line.split(',')]
                    v_col, fs_col, bs_col = curve_cols
                    try:
                        float(parts[v_col])
                        experiment['curve'].append({
                            'voltage': parts[v_col],
                            'fs': parts[fs_col] if len(parts) > fs_col else '',
                            'bs': parts[bs_col] if len(parts) > bs_col else ''
                        })
                    except (ValueError, IndexError):
                        curve_cols = None

                i += 1

            experiments.append(experiment)

        i += 1

    return experiments


def generate_metric_csv(metric_name: str, all_data: Dict[str, List[Dict]], output_path: str):
    """
    Genera un archivo CSV para una métrica específica.

    Args:
        metric_name: Nombre de la métrica (ej: 'Jsc', 'Voc')
        all_data: Diccionario con {filename: [experiments]}
        output_path: Ruta del archivo de salida
    """
    # Ordenar archivos alfabéticamente
    sorted_files = sorted(all_data.keys())

    # Encontrar el número máximo de experimentos
    max_experiments = max(len(experiments) for experiments in all_data.values())

    # Crear el CSV
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Fila 1: Nombres de archivos
        header_row1 = []
        for filename in sorted_files:
            header_row1.extend([filename, ''])
        writer.writerow(header_row1)

        # Fila 2: fs, bs repetido
        header_row2 = []
        for _ in sorted_files:
            header_row2.extend(['fs', 'bs'])
        writer.writerow(header_row2)

        # Filas de datos: una por experimento
        for exp_idx in range(max_experiments):
            row = []
            for filename in sorted_files:
                experiments = all_data[filename]
                if exp_idx < len(experiments):
                    experiment = experiments[exp_idx]
                    if metric_name in experiment:
                        row.append(experiment[metric_name]['fs'])
                        row.append(experiment[metric_name]['bs'])
                    else:
                        row.extend(['', ''])
                else:
                    row.extend(['', ''])
            writer.writerow(row)


def generate_summary_csv(all_data: Dict[str, List[Dict]], output_path: str):
    """
    Genera un archivo CSV resumen con todas las métricas.

    Args:
        all_data: Diccionario con {filename: [experiments]}
        output_path: Ruta del archivo de salida
    """
    # Ordenar archivos alfabéticamente
    sorted_files = sorted(all_data.keys())

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Header - Fila 1: Nombres de métricas
        header_row1 = ['Filename', 'Cell', 'Jsc', '', 'Voc', '', 'Fill Factor', '', 'Efficiency', '', 'Rs', '']
        writer.writerow(header_row1)

        # Header - Fila 2: fs y bs
        header_row2 = ['', '', 'fs', 'bs', 'fs', 'bs', 'fs', 'bs', 'fs', 'bs', 'fs', 'bs']
        writer.writerow(header_row2)

        # Iterar por cada archivo
        for filename in sorted_files:
            experiments = all_data[filename]

            # Cada experimento es una fila
            for experiment in experiments:
                row = [
                    filename,
                    experiment.get('comment', ''),
                    experiment.get('Jsc', {}).get('fs', ''),
                    experiment.get('Jsc', {}).get('bs', ''),
                    experiment.get('Voc', {}).get('fs', ''),
                    experiment.get('Voc', {}).get('bs', ''),
                    experiment.get('Fill Factor', {}).get('fs', ''),
                    experiment.get('Fill Factor', {}).get('bs', ''),
                    experiment.get('Efficiency', {}).get('fs', ''),
                    experiment.get('Efficiency', {}).get('bs', ''),
                    experiment.get('Rs', {}).get('fs', ''),
                    experiment.get('Rs', {}).get('bs', '')
                ]
                writer.writerow(row)


def generate_iv_curves_csv(all_data: Dict[str, List[Dict]], output_path: str):
    """
    Genera un archivo CSV con las curvas I-V (J1 = fs, J2 = bs) de cada experimento.

    Formato similar a jsc.csv, pero con un par de columnas fs/bs por experimento
    y una fila por punto de voltaje.

    Args:
        all_data: Diccionario con {filename: [experiments]}
        output_path: Ruta del archivo de salida
    """
    # Lista de (filename, experimento) en el mismo orden que summary.csv
    curves = [
        (filename, experiment)
        for filename in sorted(all_data.keys())
        for experiment in all_data[filename]
        if experiment.get('curve')
    ]

    if not curves:
        print("  Warning: no se encontraron curvas I-V")

    # Columna de voltaje: se toma de la curva con más puntos
    longest = max((exp['curve'] for _, exp in curves), key=len, default=[])
    voltages = [point['voltage'] for point in longest]

    # Avisar si alguna curva usa voltajes distintos (las filas no coincidirían)
    for filename, experiment in curves:
        curve_voltages = [point['voltage'] for point in experiment['curve']]
        if any(float(v) != float(ref) for v, ref in zip(curve_voltages, voltages)):
            print(f"  Warning: voltajes distintos en {filename} / "
                  f"{experiment.get('comment', '')}; revisar alineación de filas")

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Fila 1: nombres de archivos
        header_row1 = ['Filename']
        for filename, _ in curves:
            header_row1.extend([filename, ''])
        writer.writerow(header_row1)

        # Fila 2: celda (comentario) de cada experimento, sobre fs y sobre bs
        header_row2 = ['Cell']
        for _, experiment in curves:
            cell = experiment.get('comment', '')
            header_row2.extend([cell, cell])
        writer.writerow(header_row2)

        # Fila 3: fs, bs repetido
        header_row3 = ['Voltage / V']
        for _ in curves:
            header_row3.extend(['fs', 'bs'])
        writer.writerow(header_row3)

        # Filas de datos: una por punto de voltaje
        for idx, voltage in enumerate(voltages):
            row = [voltage]
            for _, experiment in curves:
                curve = experiment['curve']
                if idx < len(curve):
                    row.extend([curve[idx]['fs'], curve[idx]['bs']])
                else:
                    row.extend(['', ''])
            writer.writerow(row)


def main():
    """Función principal del script."""
    if len(sys.argv) < 2:
        print("Uso: python process_solar_cells.py archivo1.csv archivo2.csv ...")
        print("Ejemplo: python process_solar_cells.py *.csv")
        sys.exit(1)

    # Obtener archivos de entrada
    input_files = sys.argv[1:]

    # Parsear todos los archivos
    all_data = {}
    for filepath in input_files:
        if not Path(filepath).exists():
            print(f"Warning: Archivo no encontrado: {filepath}")
            continue

        print(f"Procesando: {filepath}")
        filename = Path(filepath).stem  # Nombre sin extensión
        experiments = parse_csv_file(filepath)
        all_data[filename] = experiments
        print(f"  Encontrados {len(experiments)} experimentos")

    if not all_data:
        print("Error: No se encontraron archivos válidos para procesar")
        sys.exit(1)

    # Generar los 4 archivos de salida
    metrics = ['Jsc', 'Voc', 'Fill Factor', 'Efficiency']
    output_files = ['jsc.csv', 'voc.csv', 'fill_factor.csv', 'efficiency.csv']

    for metric, output_file in zip(metrics, output_files):
        print(f"\nGenerando {output_file}...")
        generate_metric_csv(metric, all_data, output_file)
        print(f"  ✓ {output_file} creado")

    # Generar archivo resumen
    print(f"\nGenerando summary.csv...")
    generate_summary_csv(all_data, 'summary.csv')
    print(f"  ✓ summary.csv creado")

    # Generar archivo de curvas I-V
    print(f"\nGenerando iv_curves.csv...")
    generate_iv_curves_csv(all_data, 'iv_curves.csv')
    print(f"  ✓ iv_curves.csv creado")

    print("\n¡Proceso completado!")


if __name__ == '__main__':
    main()
