#### NEW Notes on the simulation

#### Upon reading!

### Importante take aways!

**Tudo conferido, pequenos ajustes, mas: continua índice de greens bem  maior que o reportado no artigo
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

0. IVA é usado como benchmarket para public finance.
1. Autores mencionam CUMULATIVE COSTS p.64
6. **Public expenditure is calculated using ACCUMULATED expenditures**

## TO EVALUATE STILL
5. **Do discounts and taxes paid/received by consumers affect value received by firms?**

 