## Cosa sto vedendo?

Questa **dashboard** usa i dati rilasciati quotidianamente dal Dipartimento della Protezione Civile (DPC) per rappresentare graficamente l'andamento dei casi di COVID-19 in Italia. La mappa a sinistra rappresenta per ogni provincia una delle tre misure elencate nel menù a discesa (assente nella versione mobile, *ndr*):

- **Totale casi**, come riportato dal DPC (unica misura disponibile nella versione mobile, *ndr*);
- **Variazione (abs)**, calcolata per ogni dato giorno come la differenza di casi rispetto al giorno precedente;
- **Variazione (%)**, calcolata per ogni dato giorno come il rapporto tra la variazione assoluta e il numero di casi del giorno precedente, moltiplicato per 100.

La data di interesse può essere cambiata usando il selettore a scorrimento al di sotto della mappa. Cliccando su una o più province, è possibile rappresentare l'andamento temporale della misura mostrata nella mappa. Infine, la tabella in fondo alla pagina (assente nella versione mobile, *ndr*) riporta i dettagli per la data selezionata.

La dashboard è stata realizzata in Python con *Plotly* e *Dash*, e il codice è disponibile su [GitHub](https://github.com/matteomancini/covid19ita-dash). I dati rilasciati dal DPC sono disponibili anch'essi su [GitHub](https://github.com/pcm-dpc/COVID-19) in formato CSV.

Contatti: [@matteomancini](https://github.com/matteomancini)