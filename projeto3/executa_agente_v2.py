from logsense_ia import search_logs, block_ip_firewall

print('teste do LogSense')

query = 'Ataque de injeção SQL detectado'
print(f'Investigando incidente: {query}')
resultado_busca = search_logs(query, n_results=1)

ip_suspeito = '192.168.1.1'

print(f'Ameaça detectada inciando protocolo para: {ip_suspeito}')
resultado_bloqueio = block_ip_firewall(ip_suspeito, 'Ataque de injeção SQL detectado')
print(f'Resultado do bloqueio: {resultado_bloqueio}')