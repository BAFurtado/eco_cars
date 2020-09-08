#### NEW Notes on the simulation

#### Upon reading!

0. O Cleanness do carro estava como 1/drive_range, mas é 1/emmissions. Troquei.
1. Probability adoption estava dividindo antes de elevar. Troquei.
2. Epsilon estava escolhendo o máximo entre 0 e market share green, na verdade é epsilon se 0 e share se diferente 
(pouca diferença, mas troquei.)
3. emotion estava fixo, mas o texto menciona que pode se alterar a cada t. Corrigi.
4. O texto também fala em **reajustes anuais de gas e green prices** (mas a tabela de valores é fixa). Mantido fixo.
Mas, de fato, a fórmula menciona pe_t. Teríamos que ter os dados originais de alteração para corrigir, se for o caso.
5. Formula 4 suggests PC -- production cost -- at t - 1. In the model, PC has no memory of past values. But when 
investments occur, PC is updated. Because consumers buy first, necessarily PC refer to previous period. Right?
6. A escolha de parametros para a tecnologia verde estava sendo feita entre o carro corrente a gasolina e a firma 
a imitar e não entre green t0 e a firma a imitar. Corrigi :|
1. Autores mencionam CUMULATIVE COSTS p.64
2. ROI is just previous period

6. **Public expenditure is calculated using ACCUMULATED expenditures**

4. A firma que é eliminada pode ser utilizada como imitação, dentre as alternativas aleatórias, logo depois é 
eliminada. 

## TO EVALUATE STILL
5. **Do discounts and taxes paid/received by consumers affect value received by firms?**

 