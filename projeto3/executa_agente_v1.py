from logsense_ia import search_logs, get_log_statistics, ingestao_logs_do_arquivo

print('teste do LogSense')

ingestao_logs_do_arquivo()

stats = get_log_statistics()
print(f'\n Status: {stats}')

pergunta = 'Houve alguma tentativa de injeção de SQL ?'
print(f'Pergunta para o agente {pergunta}')

resposta = search_logs(pergunta)
print(f'\n Resposta: {resposta}')




