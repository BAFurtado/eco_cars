#### Notes for the Brazilian case and hybrid cars.

### Dúvidas das implementações novas do modelo

#### Implementando HYBRID

1.             # Firms only move from gas to green and hybrid
2.             # Chooses between green or hybrid randomly
3.             PREÇOS HIBRIDO. MEDIA DOS DOIS
4.             VOLTEI EMISSIONS PARA 1 DO GREEN POR CAUSA DE DIVISÃO DE ZERO MESMO... 
E O CRITERIO FICARIA INFINITO OU MUITO GRANDE

NOVAS NOTAS DE ULTIMOS AJUSTES INCLUIDOS
** IMPORTANTE **

1. A tabela de valores do texto -- tabela 3 -- já inclui o desconto do IPI?
XXXXXXXX (Não)
2. ICMS cobrado na região de DESTINO, certo... so CONSUMIDOR! (ok)

3. IMPLEMENTADO O cashback de PD como limitado a 12.5% do investimento, comparado com TODOS OS impostos a pagar, 
   MENOS ICMS. (ok)

4. ACHO QUE O CRITERIO DE CAR AFFORDABILITY DEVERIA SER MAIS PRESENTE QUE OS DEMAIS PORQUE VAI FAZER MUITA DIFERENÇA 
   AGORA ...(como assim?)

1. Como dar dinheiro para os consumidores?
No original era 29000 com variancia de 5000, sendo o carro mais caro 27000
   Vou implementar algo similar. (ok)
   
AGORA. NORTE É MAIS POBRE, COM MENOS GENTE E FRETE MAIS CARO... I WONDER COMO O POVO LÁ DIRIGE....
MASSA SALARIAL IBGE
R. Utilizei a proporção, considerando o sudeste como 100%. E coloquei a renda como 37000 (um pouco acima do 35000),
mas vou incluir o multiplicador (redutor para regiões), com isso só, sudeste vai ter a media com mais do caro mais caro.
Vou aumentar a variância em 50% para 7500 (ok)

1. Como cobrar preços dos combustíveis para o híbrido? 
R. 50% de cada? mínimo dentre os dois? (Hy-é um automóvel que tem um motor de combustão interna (gasolina), e um motor eléctrico que permite manter o motor de combustão funcionando a baixas rotações (ou em certos momentos não funcionando). Assim, reduzir o consumo de combustível e a emissão de poluentes. Logo não pode ser 50% visto que consome menos combustivel. Eu acho que pode colocar dependendo do preço da gasolina e da energia elétrica, ouseja, o que estiver menos o consumidor escolhe).
   
2. Disponibilidade postos?
R. Igual á gasolina? (Não, é diferente, tem mais postos de combustive do que recarga. São 40.000 postos de gasolina pelo BR e mais ou menos 500 eletropostos)
   
3. Híbrido usa gas ou energia? (os 2)
R. Penso que deveríamos colocar uma probabilidade, 
   dependendo da disponibilidade de preços, ou um, ou outro. (correto)
   
r2. Alternativamente, todos podem usar etanol, né? Então se 70% da energia usa um, 
senão o outro? Já direto nos parâmetros...

4. Pis e COFINS são maiores para os menos poluentes? É isso mesmo? (é o que eu achei como dados. Só tem redução de IPI e IOF é PCD e taxistas. Os demais consumidores pagam essas txs de PIS e Cofins)

5. Vou simplificar a análise da política. Os autores originais faziam uma gradação de 
implementação da política. Vou fazer mais simples (tem, não tem) e incluir a análise de sensibilidade. (ok)
   

-------
Fábrica por Região
Região	Fábricas Automóveis
Norte    	   0
Nordeste	      3
Sudeste	      14
Sul 	         5
Centro-Oeste	2
Total 	24

  



 
