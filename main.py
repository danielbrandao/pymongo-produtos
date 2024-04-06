from config import SQLALCHEMY_DATABASE_URI, mongodb, pedidos_collection
from flask import Flask, jsonify, request
from sqlalchemy import Integer, String, Float, Date
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
mysql = SQLAlchemy(app)

class Produtos(mysql.Model):
    id_produto = mysql.Column(Integer, primary_key=True)
    nome = mysql.Column(String)
    descricao = mysql.Column(String)
    preco = mysql.Column(Float)
    categoria = mysql.Column(String)

    def serialize(self):
        return {
            "id": self.id_produto,
            "nome": self.nome,
            "descricao": self.descricao,
            "preco": self.preco,
            "categoria": self.categoria
        }

class Clientes(mysql.Model):
    id_clientes = mysql.Column(Integer, primary_key=True)
    nome = mysql.Column(String)
    email = mysql.Column(String)
    cpf = mysql.Column(String)
    data_nascimento = mysql.Column(Date)

    def serialize(self):
        return {
            "id_cliente": self.id_clientes,
            "nome": self.nome,
            "email": self.email,
            "cpf": self.cpf,
            "data_nascimento": self.data_nascimento
        }

class Pedido():
    def __init__(self, id_cliente, id_produto, data_pedido, valor_pedido):
        self.id_cliente = id_cliente
        self.id_produto = id_produto
        self.data_pedido = data_pedido
        self.valor_pedido = valor_pedido

    def serialize(self):
        return {
            "id_cliente": self.id_cliente,
            "id_produto": self.id_produto,
            "data_pedido": self.data_pedido,
            "valor_pedido": self.valor_pedido,
        }
@app.route("/", methods=['GET'])
def index():
    return '<h1>Olá, mundo.</h1>'

@app.route("/produtos", methods=['GET'])
def get_produtos():
    produtos = Produtos.query.all()
    return jsonify([produto.serialize() for produto in produtos])

@app.route("/produtos", methods=['POST'])
def set_produto():
    try:
        dados = request.get_json()
        produto = Produtos(
            nome=dados["nome"],
            descricao=dados["descricao"],
            preco=dados["preco"],
            categoria=dados["categoria"]
        )
        mysql.session.add(produto)
        mysql.session.commit()
        return jsonify(produto.serialize()), 201
    except Exception as e:
        print(f"Erro: {e}")
        return jsonify(), 400

@app.route("/produto/<int:id>", methods=["PUT"])
def update_produto(id):
    try:
        dados = request.get_json()

        produto = mysql.session.query(Produtos).get(id)
        produto.nome = dados["nome"]
        produto.descricao = dados["descricao"]
        produto.preco = dados["preco"]
        produto.categoria = dados["categoria"]

        mysql.session.commit()
        return jsonify(produto.serialize()), 201
    except Exception as e:
        print(f"Error: {e}")
        return "Erro ao alterar os dados", 400

@app.route("/produto/<int:id>", methods=["DELETE"])
def delete_produto(id):
    try:
        produto = mysql.session.query(Produtos).get(id)
        mysql.session.delete(produto)
        mysql.session.commit()
        print("Sucesso.")
        return 'Excluido com sucesso.', 204
    except Exception as e:
        print(f"Erro: {e}")
        return "Erro ao excluir produto", 400

@app.route("/clientes", methods=['GET'])
def get_clientes():
    clientes = Clientes.query.all()
    return jsonify([cliente.serialize() for cliente in clientes])

@app.route("/pedidos", methods=['POST'])
def set_pedido():
    dados = request.get_json()
    novo_pedido = Pedido(
        id_produto=dados["id_produto"],
        id_cliente=dados['id_cliente'],
        data_pedido=dados["data_pedido"],
        valor_pedido=dados["valor_pedido"]
    )
    resultado = pedidos_collection.insert_one(novo_pedido.serialize())
    if resultado.inserted_id:
        # Retorna o pedido recém-criado e o status 201
        novo_pedido.id_pedido = str(resultado.inserted_id)
        return jsonify(novo_pedido.serialize()), 201
    else:
        return "Erro ao inserir pedido.", 500

@app.route("/pedidos", methods=["GET"])
def get_pedidos():
    try:
        pedidos = pedidos_collection.find()

        # Convertendo ObjectId em strings para serialização
        pedidos_serializaveis = []
        for pedido in pedidos:
            pedido['_id'] = str(pedido['_id'])
            pedidos_serializaveis.append(pedido)

        return jsonify(pedidos_serializaveis), 200
    except Exception as e:
        print(f"Erro: {e}")
        return "Erro ao listar pedidos.", 500

if __name__ == "__main__":
    app.run(debug=True)