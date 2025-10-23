# Teste Técnico – Visão Computacional + IA 

Este projeto é um mini-aplicativo de linha de comando (CLI) construído em Python para realizar a segmentação de imagens usando dois algoritmos diferentes: Segmentação por cor em HSV e Segmentação por agrupamento (K-Means). 
## 1. Como Instalar e Rodar 

### Pré-requisitos
* Python 3.9+ 

### Instalação

1.  Clone este repositório (ou baixe e descompacte o .zip):
    ```bash
    # (Se for um repositório git)
    git clone https://github.com/LeonardVG/teste-segmentacao_ybysys.git
    cd teste-segmentacao_ybysys
    ```

2.  Crie e ative um ambiente virtual:
    ```bash
    python -m venv venv
    .\venv\Scripts\activate   # No Windows
    #source venv/bin/activate  # No Linux/macOS
    ```

3.  Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```

4.  Crie as pastas samples e outputs (se ainda não existirem):
    ```bash
    mkdir samples
    mkdir outputs
    ```
    (Coloque suas imagens de teste na pasta 'samples/'

### Como Rodar

Use o script 'segment.py' a partir do terminal.

**Exemplos de uso:**

**Método 1: Segmentação por Cor (HSV)**

* Para segmentar "verde" com os valores padrão:
    ```bash
    python segment.py --input samples/nome_da_imagem.png --method hsv --target green
    ```

* Para segmentar "azul" com ajustes finos nos limiares de Matiz (Hue): 
    ```bash
    python segment.py --input samples/nome_da_imagem.png --method hsv --target blue --hmin 90 --hmax 130
    ```

**Método 2: Segmentação por Agrupamento (K-Means)**

* Para segmentar "verde" agrupando a imagem em 3 clusters (K=3): 
    ```bash
    python segment.py --input samples/nome_da_imagem.png --method kmeans --k 3 --target green
    ```

Os resultados serão salvos na pasta `outputs/` (ex: `nome_da_imagem_mask.png` e `nome_da_imagem_overlay.png`). 

---

## 2. Explicação Breve dos Métodos 

### 1) Segmentação por Cor (HSV) 

Este método é uma abordagem manual. A imagem é convertida do espaço de cor BGR para HSV (Hue, Saturation, Value).

* **Hue (H):** Define a "cor pura" (ex: verde, azul, vermelho).
* **Saturation (S):** Define a "pureza" da cor (valores baixos são acinzentados).
* **Value (V):** Define o "brilho" da cor (valores baixos são escuros/pretos).

Definimos um intervalo de valores mínimos e máximos para H, S e V.  
O algoritmo simplesmente cria uma máscara onde os pixels brancos representam todos os pixels da imagem original cujos valores HSV caíram dentro desse intervalo

### 2) Segmentação por Agrupamento (K-Means) 

Este é um método de aprendizado de máquina não-supervisionado. Ele não usa HSV, ele analisa as cores (B, G, R) diretamente.

1.  O algoritmo agrupa todos os pixels da imagem em K clusters (grupos) diferentes. 
2.  O agrupamento é feito por proximidade da cor: pixels com cores BGR similares ficam no mesmo cluster.
3.  Após o K-Means rodar, ele nos retorna a cor "média" (centróide) de cada cluster. 
4.  O programa então calcula qual desses K centróides é o mais próximo da cor alvo (ex: [0, 255, 0] para verde) e gera a máscara selecionando todos os pixels que pertencem aquele cluster. 

---

## 3. Observações sobre Ranges HSV 


* O canal **H (Hue)** é o mais importante para definir qual cor queremos.E para verde foi escolhido a faixa de **40 até 80**, e para azul a faixa de **85 até 130**.
* O canal **S (saturação)** teve sua faixa definida de **50 até 255**, para ignorar pixels brancos, cinzas e muito "lavados", que têm baixa saturação, mas poderiam ter qualquer Hue
* O canal **V (valor)** também teve sua faixa definida de **50 até 255**, para conseguir ignorar pixels em sombras muito escuras, que tem baixo brilho.

---

## 4. Limitações Conhecidas 

Ambos os métodos possuem limitações, especialmente em cenários complexos do mundo real.Uma dessas limitações são:

* **Iluminação:** Uma mudança drástica na luz solar pode mudar os valores 'V' e 'S' de um objeto, fazendo ele sair do range HSV configurado.
* **Sombras:**  Um objeto, por exemplo uma folha verde em uma sombra forte terá um valor 'V' muito baixo. Isso torna difícil distinguir de outros objetos escuros como terra preta, que também têm baixo 'V'.
* **Saturação Baixa:**  Objetos de cor "lavada" podem ser difíceis de segmentar. Um verde muito pálido, um azul muito pálido e um cinza-claro são quase idênticos no espaço HSV.
* **Sensibilidade do K-Means:** O método K-Means é muito sensível ao valor de 'K'. Se você escolher 'K=2' para uma imagem que tem 3 cores dominantes (ex: planta, céu, solo), o algoritmo irá forçar a agrupar duas dessas cores em um único cluster, levando a um resultado ruim.
