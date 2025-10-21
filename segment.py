import argparse
import sys
import cv2          #openCV
import numpy as np
import time
from pathlib import Path

def segmentar_hsv(img, args):
### H - matiz -> 0-179
### S - saturação -> 0-255
### V - brilho -> 0-255
    
    print(f"LOG: iniciando Segmentação HSV para o target {args.target}")
    
    #convertendo iagem que foi aberta e eta no padrao BGR para HSV
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    #faixa padrão para verde
    if (args.target == "green"):
        h_min_padrao, h_max_padrao = (40,80)
        s_min_padrao, s_max_padrao = (50,255)
        v_min_padrao, v_max_padrao = (50,255)

    elif (args.target == "blue"):
        h_min_padrao, h_max_padrao = (85,130)
        s_min_padrao, s_max_padrao = (50,255)
        v_min_padrao, v_max_padrao = (50,255)

##### sobrescrever os padrões com os argumentos da CLI se fornecidos, se for None usa o padrão
    h_min = args.hmin if args.hmin is not None else h_min_padrao
    h_max = args.hmax if args.hmax is not None else h_max_padrao
    s_min = args.smin if args.smin is not None else s_min_padrao
    s_max = args.smax if args.smax is not None else s_max_padrao
    v_min = args.vmin if args.vmin is not None else v_min_padrao
    v_max = args.vmax if args.vmax is not None else v_max_padrao

    print(f"LOG: Ranges utilizados:H={h_min}-{h_max}, S={s_min}-{s_max}, V={v_min}-{v_max}")

    #criando arrays com os limites
    limite_inferior = np.array([h_min, s_min, v_min])
    limite_superior = np.array([h_max, s_max, v_max])

    #pintar de branco os pixels que estão dentro dos limites e o resto de preto
    mask = cv2.inRange(img_hsv, limite_inferior, limite_superior)


    return mask



def segmentar_kmeans(img,args):

    print("LOG: Chamando segmentar_por_hsv (ainda não implementado)")
    altura, largura = img.shape[:2]
    mask = np.zeros((altura, largura), dtype=np.uint8)
    
    return mask


def main():

    parser = argparse.ArgumentParser(description="Mini-aplicativo de linha de comando (CLI) pra segmentação de imagem ") 


####### Argumento de entrada ######### 
    parser.add_argument(
        '--input', 
        type=str, 
        required=True,                               # para o método de entrada ser obrigatorio
        help="Caminho para a imagem de entrada" 
    )

######### Argumento para escolher método de segmentação ###########
    parser.add_argument(
        '--method',
        type=str,
        required=True,
        choices=['hsv', 'kmeans'], 
        help="Método de segmentação a ser utilizado: hsv ou kmeans" 
    )
    
 ######### Argumento para escolher a cor alvo #############    
    parser.add_argument(
        '--target',
        type=str,
        default='green', 
        choices=['green', 'blue'], 
        help="Cor alvo para a segmentação: green ou blue" 
    )

######### Argumento especificos do K-Means ##############
    parser.add_argument(
        '--k',
        type=int,
        default=3, # Valor padrão razoável
        help="Número de clusters (K) para o método K-Means" 
    )

##########  argumentos específicos do HSV (ranges) ################
    hsv_grupo = parser.add_argument_group('Ajustes finos para --method hsv') #agrupar todos os arg do hsv
    
    hsv_grupo.add_argument('--hmin', type=int, help="Valor mínimo de matiz [0-179]") 
    hsv_grupo.add_argument('--hmax', type=int, help="Valor máximo de matiz [0-179]") 
    hsv_grupo.add_argument('--smin', type=int, help="Valor mínimo de Saturação [0-255]") 
    hsv_grupo.add_argument('--smax', type=int, help="Valor máximo de Saturação [0-255]") 
    hsv_grupo.add_argument('--vmin', type=int, help="Valor mínimo de Valor [0-255]") 
    hsv_grupo.add_argument('--vmax', type=int, help="Valor máximo de Valor [0-255]") 
    
##### Analisar os argumentos ##########
    args = parser.parse_args()

    ############# TESTE #############
    print("--- Configuração da Execução ---")
    print(f"Imagem de Entrada: {args.input}")
    print(f"Método: {args.method}")
    print(f"Cor Alvo: {args.target}")

    if args.method == 'kmeans':
        print(f"Clusters K: {args.k}")
    
    if args.method == 'hsv':
        print("Limiares HSV personalizados:")
        print(f"  H: {args.hmin}-{args.hmax}")
        print(f"  S: {args.smin}-{args.smax}")
        print(f"  V: {args.vmin}-{args.vmax}")
    print("---------------------------------\n")



##### iniciar o conometro #######
    inicio_time = time.time()

    #carregar imagem
    print(f"LOG: Carregando a imagem de '{args.input}'")
    img = cv2.imread(args.input)

    if img is None:
        print("ERRO: verifique o camiho fornecido para a imagem.")
        exit(1)

    mask = None
    pastaSaida = "outputs"

    if (args.method) =='hsv':
        mask = segmentar_hsv(img, args)

    elif(args.method) == 'kmeans':
        mask = segmentar_kmeans(img,args)


### caminho para a saida
    nome_arq_input = Path(args.input).stem

    mask_caminho = f"{pastaSaida}/{nome_arq_input}_mask.png"
    overlay_caminho = f"{pastaSaida}/{nome_arq_input}_overlay.png"

    print(f"LOG: Salvando a mascara em '{mask_caminho}'")
    cv2.imwrite(mask_caminho, mask)

    print(f"LOG:Criando e salvando overlay em '{overlay_caminho}'")
    overlay = cv2.bitwise_and(img,img, mask=mask)
    cv2.imwrite(overlay_caminho,overlay)


############## Pegar as informaçoes para o log ####################
    fim_time = time.time()
    temp_execucao = fim_time - inicio_time

    total_pixels = mask.size
    pixels_segmentados = cv2.countNonZero(mask)
    porcentagem_px = (pixels_segmentados/total_pixels) * 100

    print("\n ===== Resultados =====\n")
    print(f"tempo total de execução: {temp_execucao:.5}\n")
    print(f"Percentuais de pixels segmentados: {porcentagem_px}% ({pixels_segmentados} de {total_pixels})\n")
    print(f"Máscara salva em: {mask_caminho}\n")
    print(f"Overlay salvo em: {overlay_caminho}\n")



if __name__ == "__main__":
    main()