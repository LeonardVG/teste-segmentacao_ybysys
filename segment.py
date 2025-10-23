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

###################################################################################################################################

def segmentar_kmeans(img,args):
    print(f"LOG: iniciando segmentação K-means com k={args.k} e alvo '{args.target}'")

    altura = img.shape[0]
    largura = img.shape[1]

    #achatando pq o kmeans do opencv aceita só 2D
    #uma lista de pontos (pixels) com cada ponto tendo suas caractwristicas (cores rgb)
    pixels_img = img.reshape((-1,3))
    #converter pra float32 pq o opencv exige
    pixels_img = np.float32(pixels_img)

    k = args.k

    #criterio de parada (tipo, max_interações,precisão)
    criterio = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)

    #rodar o alg 10 vezes com centros iniciais aleatorios para escolher o melhor
    tentativas = 10
    flag = cv2.KMEANS_RANDOM_CENTERS

    #execurar o k-means
    soma_distancias, grupo_q_pertence, cor_media_clausters = cv2.kmeans(
        data=pixels_img,
        K=k,
        bestLabels= None,
        criteria=criterio,
        attempts= tentativas,
        flags=flag
    )

    print(f"LOG: K-Means concluído. Centróides encontrados:")
    # Converte centróides para inteiros para impressão
    print(cor_media_clausters.astype(int))

    if args.target == 'green':
        target_cor = np.array([0,255,0],dtype=np.float32)
    elif args.target == 'blue':
        target_cor = np.array([255,0,0], dtype=np.float32)

    dist_min = float('inf')
    id_clauster_maisproxAlvo = -1

    #olhar cada centroide para ver qual ta mais proximo da cor desejada
    for i in range(k):
        cor_centroid = cor_media_clausters[i]

        distancia = np.linalg.norm(cor_centroid - target_cor)

        if distancia < dist_min:
            dist_min = distancia
            id_clauster_maisproxAlvo = i

    
    print(f"LOG: Cluster alvo selecionado: {id_clauster_maisproxAlvo} (Cor: {cor_media_clausters[id_clauster_maisproxAlvo].astype(int)})")

    #criar mascara
    mask_plana = (grupo_q_pertence.flatten() == id_clauster_maisproxAlvo)
    #converter True pra 255 e false pra 0 e para o tipo imagem uint8
    mask_uint8 = np.uint8(mask_plana * 255)

    #desatachar a imgem
    mask = mask_uint8.reshape((altura,largura))


    return mask


##########################################################################################################################################

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
        default=2, # valor padrão razoável
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
    nome_arq_input = Path(args.input).stem #pega só o nome do arq

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