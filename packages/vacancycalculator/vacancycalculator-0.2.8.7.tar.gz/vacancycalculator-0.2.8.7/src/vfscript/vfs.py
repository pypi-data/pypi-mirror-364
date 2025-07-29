# main.py

from .core import *  
from .config_loader import cargar_json_usuario
from pathlib import Path
import os
import pandas as pd
import warnings
warnings.filterwarnings('ignore', message='.*OVITO.*PyPI')

def VacancyAnalysis():
    generator = AtomicGraphGenerator()
    generator.run()
    base = "outputs"
    for sub in ("csv", "dump", "json"):
        os.makedirs(os.path.join(base, sub), exist_ok=True)

    CONFIG = cargar_json_usuario()
    
    if "CONFIG" not in CONFIG or not isinstance(CONFIG["CONFIG"], list) or len(CONFIG["CONFIG"]) == 0:
        raise ValueError("input_params.json debe contener una lista 'CONFIG' con al menos un objeto.")

    configuracion = CONFIG["CONFIG"][0]
    defect_file = configuracion['defect']
    if  configuracion['training']: 
        processor = TrainingProcessor()
        processor.run()

    

    cs_out_dir = Path("inputs")
    cs_generator = CrystalStructureGenerator(configuracion, cs_out_dir)
    dump_path = cs_generator.generate()
    print(f"Estructura relajada generada en: {dump_path}")

    processor = ClusterProcessor(defect_file)
    processor.run()
    separator = KeyFilesSeparator(configuracion, os.path.join("outputs/json", "clusters.json"))
    separator.run()

    # 3. Procesar dumps críticos
    clave_criticos = ClusterDumpProcessor.cargar_lista_archivos_criticos("outputs/json/key_archivos.json")
    for archivo in clave_criticos:
        try:
            dump_proc = ClusterDumpProcessor(archivo, decimals=5)
            dump_proc.load_data()
            dump_proc.process_clusters()
            dump_proc.export_updated_file(f"{archivo}_actualizado.txt")
        except Exception as e:
            print(f"Error procesando {archivo}: {e}")

    # 4. Subdivisión iterativa
    lista_criticos = ClusterDumpProcessor.cargar_lista_archivos_criticos("outputs/json/key_archivos.json")
    for archivo in lista_criticos:
        machine_proc = ClusterProcessorMachine(archivo, configuracion['cluster tolerance'], configuracion['iteraciones_clusterig'])
        machine_proc.process_clusters()
        machine_proc.export_updated_file()

    # 5. Separar archivos finales vs críticos
    separator = KeyFilesSeparator(configuracion, os.path.join("outputs/json", "clusters.json"))
    separator.run()

    # 6. Generar nuevos dumps por cluster
    export_list = ExportClusterList("outputs/json/key_archivos.json")
    export_list.process_files()

    # 7. Calcular superficies de dump
    surf_proc = SurfaceProcessor(configuracion)
    surf_proc.process_all_files()
    surf_proc.export_results()





#####CLASIFICACION DE DEFECTOS



    classifier = VacancyClassifier(
        json_file1='outputs/json/training_data.json',
        json_file2='outputs/json/training_graph.json',
        merged_json='outputs/json/merged_training.json',
        csv_input='outputs/csv/defect_data.csv',
        csv_output='outputs/csv/defect_data_classified.csv'
    )
    classifier.merge_json()
    classifier.train()
    classifier.classify_defects()











if __name__ == "__main__":
    VacancyAnalysis()
    print("Script ejecutado correctamente.")



