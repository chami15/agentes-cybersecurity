import asyncio
import zmq
import zmq.asyncio
from rich.live import Live
from rich.table import Table
from rich.layout import Layout
from rich.panel import Panel
from rich import box

class DashboardApp:
    def __init__(self):
        
        self.ctx = zmq.asyncio.Context()
        self.sub_socket = self.ctx.socket(zmq.SUB)
        self.sub_socket.connect('tcp://localhost:5555')
        self.sub_socket.connect('tcp://localhost:5556')
        self.sub_socket.subscribe("")
        self.logs_table = Table(title='App Live Log Stream', box = box.SIMPLE, style= 'dim', expand=True)
        self.logs_table.add_column("Hora", style = "cyan", width = 10)
        self.logs_table.add_column("Origem", style = "magenta", width = 15)
        self.logs_table.add_column("Conteúdo", style = "white")
        self.alerts_table = Table(title="Ameaças Detectadas", box = box.HEAVY_EDGE, style = "red", expand = True)
        self.alerts_table.add_column("Severidade", style = "bold red", width = 10)
        self.alerts_table.add_column("Categoria", style = "yellow", width = 20)
        self.alerts_table.add_column("AI Reasoning", style="white")
        self.fix_panel = Panel("Aguardando o tráfego para analisar ameaças na app...", title = "Plano de Ação", border_style = "white")

    def get_layout(self):
        layout = Layout()

        layout.split_column(
            Layout(name='top', ratio=4),
            Layout(name='middle', ratio=4),
            Layout(name='bottom', ratio=3)
        )

        layout['top'].update(Panel(self.logs_table, title="input stream do AgenteOps e DevSecOps"))
        layout['middle'].update(Panel(self.alerts_table, title= "Analise feita por Agente de IA"))
        layout['bottom'].update(self.fix_panel)
        return layout
    
    async def run(self):
        print('Dashboard conectando. Aguardando...')

        with Live(self.get_layout(), refresh_per_second=4, screen=True) as live:
            while True:
                packet = await self.sub_socket.recv_json()

                if packet['type'] == 'LOG':
                    self.logs_table.add_row(
                        packet.get('timestamp', '?'),
                        packet.get('source', '?'),
                        packet.get('raw_log', '?')[:60]
                    )
                    
                    if len(self.logs_table.rows) > 6: self.logs_table.rows.pop(0)

                elif packet["type"] == "ALERT":
                
                    triage = packet.get("triage", {})
                    severity = triage.get("severity", "UNK")
                    category = triage.get("category", "Unknown")
                    reasoning = triage.get("reasoning", "")
                    
                    self.alerts_table.add_row(severity, category, reasoning[:90])

                    if len(self.alerts_table.rows) > 6: self.alerts_table.rows.pop(0)

                    remediation = packet.get("remediation")
                    if remediation:
                        content = f'[bold]Action:[/bold] {remediation.get('action_plan')}\n\n[bold]Code/Command:[/bold]\n```\n{remediation.get('code_fix')}\n```'
                        self.fix_panel = Panel(content, title='AI Auto-Fix proposal', border_style='green')
                    else: 
                        content = f'[bold]Analysis:[/bold] Threat Detected ({severity}).\n[dim]No automated fix available for this category. Manual review required.[/dim]'
                        border = 'red' if severity in ['HIGH', 'CRITICAL'] else 'yellow'
                        self.fix_panel = Panel(content, title='Manuel Review', border_style=border )
                live.update(self.get_layout())

if __name__ == '__main__':
    app = DashboardApp()
    try: 
        asyncio.run(app.run())
    except KeyboardInterrupt:
        pass
