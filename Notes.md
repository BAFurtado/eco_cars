#### NEW Notes on the simulation

#### Upon reading!

### Importante take aways!

Ultimos updates 29/9:

1. Implementada policy_value no budget das firmas
2. Incluida taxa de desconto por tempo no ROI.
3. Public expenditure é anual, não cumulativa...

** Nova rodada de conferência para September 29.

1. Continuo sem saber como implementar a linha do item C.22: "Firm i will decide to abandon technology j 
according to probabilities that depend on ROIij
and **the total number of periods** in which the firm has developed technology j: the lower the return on
investment of technology j, the higher its probability of being abandoned, and the **longer the experience
has lasted, the harder it is to abandon**"


2. Segunda coisa mais relevante, penso, é o IVA a ser descontado do preço do imóvel e recolhido para ente público.
Based on this as well: "The VAT benefits are used as a benchmark for the other
scenarios with government regulation.36" 4.1



**Tudo conferido, pequenos ajustes, mas: continua índice de greens maior que o reportado no artigo
**

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
7. Conferido pela segunda vez. Autores mencionam no item C.2.2 que quanto mais tempo investido em um carro, menor chance
de abandonar portfólio, mas isso não condiz com a fórmula e afirmação que ROI é do período anterior. 
8. Firmas que quebraram não podem mais serem imitadas
9. Como no início os carros são praticamente iguais, as firmas em primeiro lugar da lista estavam sendo sempre 
escolhidas. Alterei para embaralhar a lista antes de utilizar os critérios para compra, para evitar o caso em que os 
critérios são iguais.
10. A marcação de não mudança de portfólio de 10 anos vale para qualquer mudança. Portanto, só pode abandonar 'gas' no
ano 20. Implementada correção.
11. As vezes, mesmo criteria era usado duas vezes, substitui random.choices por random.sample

#### ROI maior que 1. Verificar. Production_cost reduction does not affect sales prices?

0. IVA é usado como benchmarket para public finance.
1. Autores mencionam CUMULATIVE COSTS p.64
6. **Public expenditure is calculated using ACCUMULATED expenditures**

## TO EVALUATE STILL
5. **Do discounts and taxes paid/received by consumers affect value received by firms?**

 