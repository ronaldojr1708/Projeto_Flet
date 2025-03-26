import flet as ft 
import uuid
import json
from datetime import datetime

class Cliente:
    def __init__(self, nome, telefone, email):
        self.id = str(uuid.uuid4())
        self.nome = nome
        self.telefone = telefone
        self.email = email

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "telefone": self.telefone,
            "email": self.email
        }

class Quarto:
    def __init__(self, numero, tipo, preco):
        self.numero = numero
        self.tipo = tipo
        self.preco = preco
        self.disponivel = True

    def to_dict(self):
        return {
            "numero": self.numero,
            "tipo": self.tipo,
            "preco": self.preco,
            "disponivel": self.disponivel
        }

class Reserva:
    def __init__(self, cliente, quarto, checkin, checkout):
        self.id = str(uuid.uuid4())
        self.cliente = cliente
        self.quarto = quarto
        self.checkin = checkin
        self.checkout = checkout
        self.status = "Ativa"
        self.valor_total = self.calcular_valor()

    def calcular_valor(self):
        dias = (self.checkout - self.checkin).days
        return dias * self.quarto.preco

    def to_dict(self):
        return {
            "id": self.id,
            "cliente_id": self.cliente.id,
            "quarto_numero": self.quarto.numero,
            "checkin": self.checkin.strftime("%d/%m/%Y"),
            "checkout": self.checkout.strftime("%d/%m/%Y"),
            "status": self.status,
            "valor_total": self.valor_total
        }

class Gerenciador:
    def __init__(self):
        self.clientes = []
        self.quartos = []
        self.reservas = []
        self.carregar_dados()

    def salvar_dados(self):
        dados = {
            "clientes": [c.to_dict() for c in self.clientes],
            "quartos": [q.to_dict() for q in self.quartos],
            "reservas": [r.to_dict() for r in self.reservas]
        }
        with open("dados.json", "w") as f:
            json.dump(dados, f, indent=4)

    def carregar_dados(self):
        try:
            with open("dados.json", "r") as f:
                dados = json.load(f)
                self.clientes = [Cliente(c["nome"], c["telefone"], c["email"]) for c in dados["clientes"]]
                
                self.quartos = []
                for q in dados["quartos"]:
                    quarto = Quarto(q["numero"], q["tipo"], q["preco"])
                    quarto.disponivel = q["disponivel"]
                    self.quartos.append(quarto)
                
                self.reservas = []
                for r in dados["reservas"]:
                    cliente = next(c for c in self.clientes if c.id == r["cliente_id"])
                    quarto = next(q for q in self.quartos if q.numero == r["quarto_numero"])
                    checkin = datetime.strptime(r["checkin"], "%d/%m/%Y")
                    checkout = datetime.strptime(r["checkout"], "%d/%m/%Y")
                    
                    reserva = Reserva(cliente, quarto, checkin, checkout)
                    reserva.status = r["status"]
                    self.reservas.append(reserva)
        except:
            pass

    def adicionar_cliente(self, cliente):
        self.clientes.append(cliente)
        self.salvar_dados()

    def remover_cliente(self, cliente_id):
        self.clientes = [c for c in self.clientes if c.id != cliente_id]
        self.salvar_dados()

    def adicionar_quarto(self, quarto):
        self.quartos.append(quarto)
        self.salvar_dados()

    def quartos_disponiveis(self):
        return [q for q in self.quartos if q.disponivel]

    def fazer_reserva(self, cliente, quarto, checkin, checkout):
        reserva = Reserva(cliente, quarto, checkin, checkout)
        quarto.disponivel = False
        self.reservas.append(reserva)
        self.salvar_dados()
        return reserva

def main(page: ft.Page):
    page.title = "Hotel Refúgio dos Sonhos"
    page.theme_mode = ft.ThemeMode.DARK
    gerenciador = Gerenciador()
    
    
    resultado = ft.Text()
    
    nome_cliente = ft.TextField(label="Nome Completo")
    tel_cliente = ft.TextField(label="Telefone")
    email_cliente = ft.TextField(label="E-mail")
    
    tbl_clientes = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Nome")),
            ft.DataColumn(ft.Text("Telefone")),
            ft.DataColumn(ft.Text("E-mail")),
            ft.DataColumn(ft.Text("Ações"))
        ]
    )
    
    def carregar_clientes():
        tbl_clientes.rows = []
        for cliente in gerenciador.clientes:
            tbl_clientes.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(cliente.nome)),
                        ft.DataCell(ft.Text(cliente.telefone)),
                        ft.DataCell(ft.Text(cliente.email)),
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(ft.icons.EDIT, on_click=lambda e, c=cliente: editar_cliente(c)),
                                ft.IconButton(ft.icons.DELETE, icon_color="red", 
                                            on_click=lambda e, c=cliente: remover_cliente(c))
                            ])
                        )
                    ]
                )
            )
        page.update()
    
    def cadastrar_cliente(e):
        if not all([nome_cliente.value, tel_cliente.value, email_cliente.value]):
            resultado.value = "Preencha todos os campos!"
            page.update()
            return
            
        cliente = Cliente(nome_cliente.value, tel_cliente.value, email_cliente.value)
        gerenciador.adicionar_cliente(cliente)
        carregar_clientes()
        limpar_campos_clientes()
        resultado.value = "Cadastrado efetuado com sucesso!"
        page.update()
    
    def remover_cliente(cliente):
        gerenciador.remover_cliente(cliente.id)
        carregar_clientes()
        resultado.value = "Cliente removido!"
        page.update()
    
    def editar_cliente(cliente):
        nome_cliente.value = cliente.nome
        tel_cliente.value = cliente.telefone
        email_cliente.value = cliente.email
        page.update()
    
    def limpar_campos_clientes():
        nome_cliente.value = ""
        tel_cliente.value = ""
        email_cliente.value = ""
    
    numero_quarto = ft.TextField(label="Número", input_filter=ft.NumbersOnlyInputFilter())
    tipo_quarto = ft.Dropdown(
        label="Tipo",
        options=[
            ft.dropdown.Option("Casal"),
            ft.dropdown.Option("Solteiro"),
            ft.dropdown.Option("Presidencial")
        ]
    )
    preco_quarto = ft.TextField(label="Preço Diária", input_filter=ft.NumbersOnlyInputFilter())
    
    tbl_quartos = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Número")),
            ft.DataColumn(ft.Text("Tipo")),
            ft.DataColumn(ft.Text("Preço")),
            ft.DataColumn(ft.Text("Disponível")),
            ft.DataColumn(ft.Text("Ações"))
        ]
    )
    
    def carregar_quartos():
        tbl_quartos.rows = []
        for quarto in gerenciador.quartos:
            tbl_quartos.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(quarto.numero))),
                        ft.DataCell(ft.Text(quarto.tipo)),
                        ft.DataCell(ft.Text(f"R$ {quarto.preco:.2f}")),
                        ft.DataCell(ft.Text("Sim" if quarto.disponivel else "Não")),
                        ft.DataCell(
                            ft.IconButton(ft.icons.DELETE, icon_color="red",
                                        on_click=lambda e, q=quarto: remover_quarto(q))
                        )
                    ]
                )
            )
        page.update()
    
    def cadastrar_quarto(e):
        if not all([numero_quarto.value, tipo_quarto.value, preco_quarto.value]):
            resultado.value = "Preencha todos os campos!"
            page.update()
            return
            
        try:
            quarto = Quarto(
                numero = int(numero_quarto.value),
                tipo = tipo_quarto.value,
                preco = float(preco_quarto.value)
            )
            gerenciador.adicionar_quarto(quarto)
            carregar_quartos()
            limpar_campos_quartos()
            resultado.value = "Quarto cadastrado!"
            page.update()
        except Exception as ex:
            resultado.value = f"Erro: {str(ex)}"
            page.update()
    
    def remover_quarto(quarto):
        gerenciador.quartos.remove(quarto)
        gerenciador.salvar_dados()
        carregar_quartos()
        resultado.value = "Quarto removido!"
        page.update()
    
    def limpar_campos_quartos():
        numero_quarto.value = ""
        tipo_quarto.value = ""
        preco_quarto.value = ""
    
    cliente_reserva = ft.Dropdown(label="Cliente")
    quarto_reserva = ft.Dropdown(label="Disponível")
    checkin = ft.TextField(label="Check-in (dd/mm/aaaa)")
    checkout = ft.TextField(label="Check-out (dd/mm/aaaa)")
    valor_total = ft.Text("Valor Total: R$ 0.00", size=16, color=ft.colors.GREEN)
    
    tbl_reservas = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Cliente")),
            ft.DataColumn(ft.Text("Quarto")),
            ft.DataColumn(ft.Text("Período")),
            ft.DataColumn(ft.Text("Valor")),
            ft.DataColumn(ft.Text("Status"))
        ]
    )
    
    def carregar_reservas():
        tbl_reservas.rows = []
        for reserva in gerenciador.reservas:
            tbl_reservas.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(reserva.cliente.nome)),
                        ft.DataCell(ft.Text(f"{reserva.quarto.numero} ({reserva.quarto.tipo})")),
                        ft.DataCell(ft.Text(f"{reserva.checkin.strftime('%d/%m/%Y')} a {reserva.checkout.strftime('%d/%m/%Y')}")),
                        ft.DataCell(ft.Text(f"R$ {reserva.valor_total:.2f}")),
                        ft.DataCell(ft.Text(reserva.status))
                    ]
                )
            )
        page.update()
    
    def carregar_opcoes_reserva():
        cliente_reserva.options = [
            ft.dropdown.Option(f"{c.nome} - {c.telefone}") for c in gerenciador.clientes
        ]
        quarto_reserva.options = [
            ft.dropdown.Option(f"{q.numero} - {q.tipo}") for q in gerenciador.quartos_disponiveis()
        ]
        page.update()
    
    def calcular_total(e):
        try:
            checkin_date = datetime.strptime(checkin.value, "%d/%m/%Y")
            checkout_date = datetime.strptime(checkout.value, "%d/%m/%Y")
            
            if checkin_date >= checkout_date:
                raise ValueError("Check-out deve ser após check-in")
            
            quarto_num = int(quarto_reserva.value.split(" - ")[0])
            quarto = next(q for q in gerenciador.quartos if q.numero == quarto_num)
            
            dias = (checkout_date - checkin_date).days
            total = dias * quarto.preco
            valor_total.value = f"Valor Total: R$ {total:.2f}"
            page.update()
        except Exception as ex:
            resultado.value = f"Erro: {str(ex)}"
            page.update()
    
    def finalizar_reserva(e):
        try:
            cliente_nome = cliente_reserva.value.split(" - ")[0]
            cliente = next(c for c in gerenciador.clientes if c.nome == cliente_nome)
            
            quarto_num = int(quarto_reserva.value.split(" - ")[0])
            quarto = next(q for q in gerenciador.quartos if q.numero == quarto_num)
            
            checkin_date = datetime.strptime(checkin.value, "%d/%m/%Y")
            checkout_date = datetime.strptime(checkout.value, "%d/%m/%Y")
            
            if checkin_date >= checkout_date:
                raise ValueError("Data de check-in inválida")
            
            gerenciador.fazer_reserva(cliente, quarto, checkin_date, checkout_date)
            
            carregar_quartos()
            carregar_opcoes_reserva()
            carregar_reservas()
            limpar_campos_reserva()
            resultado.value = "Reserva realizada com sucesso!"
            page.update()
        except Exception as ex:
            resultado.value = f"Erro na reserva: {str(ex)}"
            page.update()
    
    def limpar_campos_reserva():
        cliente_reserva.value = ""
        quarto_reserva.value = ""
        checkin.value = ""
        checkout.value = ""
        valor_total.value = "Valor Total: R$ 0.00"
    
    relatorio_tipo = ft.Dropdown(
        label="Tipo de Relatório",
        options=[
            ft.dropdown.Option("Ocupação"),
            ft.dropdown.Option("Financeiro")
        ]
    )
    
    tbl_relatorios = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Descrição")),
            ft.DataColumn(ft.Text("Valor"))
        ]
    )
    
    def gerar_relatorio(e):
        if relatorio_tipo.value == "Ocupação":
            ocupacao = sum(1 for q in gerenciador.quartos if not q.disponivel)
            total = len(gerenciador.quartos)
            tbl_relatorios.rows = [
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text("Taxa de Ocupação")),
                    ft.DataCell(ft.Text(f"{(ocupacao/total)*100:.1f}%"))
                ])
            ]
        elif relatorio_tipo.value == "Financeiro":
            receita = sum(r.valor_total for r in gerenciador.reservas)
            tbl_relatorios.rows = [
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text("Receita Total")),
                    ft.DataCell(ft.Text(f"R$ {receita:.2f}"))
                ])
            ]
        page.update()
    
    page.add(
        ft.Tabs(
            tabs=[
                ft.Tab(
                    text="👤 Clientes",
                    content=ft.Column([
                        ft.Row([nome_cliente, tel_cliente, email_cliente]),
                        ft.ElevatedButton("Cadastrar Cliente", on_click=cadastrar_cliente),
                        ft.Divider(),
                        tbl_clientes
                    ])
                ),
                ft.Tab(
                    text="🛏 Quartos",
                    content=ft.Column([
                        ft.Row([numero_quarto, tipo_quarto, preco_quarto]),
                        ft.ElevatedButton("Cadastrar Quarto", on_click=cadastrar_quarto),
                        ft.Divider(),
                        tbl_quartos
                    ])
                ),
                ft.Tab(
                    text="📅 Reservas",
                    content=ft.Column([
                        ft.Row([
                            cliente_reserva,
                            quarto_reserva,
                            ft.Column([checkin, checkout])
                        ]),
                        ft.Row([
                            ft.ElevatedButton("Carregar Opções", on_click=lambda e: carregar_opcoes_reserva()),
                            ft.ElevatedButton("Calcular Total", on_click=calcular_total),
                            valor_total
                        ]),
                        ft.ElevatedButton("Confirmar Reserva", on_click=finalizar_reserva),
                        ft.Divider(),
                        ft.Text("Reservas Ativas:", weight="bold"),
                        tbl_reservas  
                    ])
                ),
                ft.Tab(
                    text="📊 Relatórios",
                    content=ft.Column([
                        ft.Row([relatorio_tipo, ft.ElevatedButton("Gerar", on_click=gerar_relatorio)]),
                        ft.Divider(),
                        tbl_relatorios
                    ])
                )
            ],
            expand=True
        ),
        resultado
    )
    
    carregar_clientes()
    carregar_quartos()
    carregar_opcoes_reserva()
    carregar_reservas()

if __name__ == "__main__":
    ft.app(target=main)



