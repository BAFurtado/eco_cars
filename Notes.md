### To check

1. Oferta acontece antes das primeiras compras. Portanto, market share e profits na primeira rodada de offer() 
são zeros. Neste caso, o **budget** não está sendo descontado do custo fixo de 25,000 
2. Só está ocorrendo bankrupt no momento 0 (quando ainda não venderam nenhum veículo).
3. A firma que é eliminada pode ser utilizada como imitação, dentre as alternativas aleatórias, logo depois é 
eliminada. Há problema?
4. Nota. O dk só começa a fazer sentido quando é implementado o carro 'green'. Todos veículos a gas tem autonomia máxima
5. Como a oferta acontece primeiro, na hora do cálculo do ROI, os veículos vendidos precisam ser do t anterior (t -1), 
pela fórmula, o investimento também é t-1, teria que ser t - 2? Implementado como **t-2**
