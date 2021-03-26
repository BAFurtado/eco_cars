#### Notes for the Brazilian case and hybrid cars.

### Dúvidas das implementações novas do modelo

#### Implementando HYBRID

1.             # Firms only move from gas to green and hybrid
2.             # Chooses between green or hybrid randomly
3.             # Hybrid prices follow gas prices
   Hy-é um automóvel que tem um motor de combustão interna (gasolina), e um motor eléctrico que permite manter o motor 
   de combustão funcionando a baixas rotações (ou em certos momentos não funcionando). Assim, reduzir o consumo de 
   combustível e a emissão de poluentes. Logo não pode ser 50% visto que consome menos combustivel. Eu acho que pode 
   colocar dependendo do preço da gasolina e da energia elétrica, ouseja, o que estiver menos o consumidor escolhe).
4.             # State consumption ICMS charged at destin
5.             # Purchasing capacity is referenced at SE region at 100. Others are weighted using official IBGE data.

*. Affordability criteria weight?
*. Disponibilidade postos?
R. Igual á gasolina? (Não, é diferente, tem mais postos de combustive do que recarga. São 40.000 postos de gasolina pelo BR e mais ou menos 500 eletropostos)
   
*. Híbrido usa gas ou energia? (os 2)
R. Penso que deveríamos colocar uma probabilidade, dependendo da disponibilidade de preços, ou um, ou outro. (correto)
