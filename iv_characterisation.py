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
        header_row1 = ['Filename', 'Cell', 'Jsc', '', 'Voc', '', 'Fill Factor', '', 'Efficiency', '']
        writer.writerow(header_row1)

        # Header - Fila 2: fs y bs
        header_row2 = ['', '', 'fs', 'bs', 'fs', 'bs', 'fs', 'bs', 'fs', 'bs']
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
                    experiment.get('Efficiency', {}).get('bs', '')
                ]
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

    print("\n¡Proceso completado!")


if __name__ == '__main__':
    main()
