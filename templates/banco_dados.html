{% extends "base.html" %}

{% block title %}PTBDSWS - Banco de Dados{% endblock %}

{% block page_content %}
<div class="page-header">
    <h1>Banco de Dados</h1>
    <p class="lead">Usando SQLite para guardar nomes</p>
</div>

<div class="row">
    <div class="col-md-8 col-md-offset-2">
        {# Exibição do nome #}
        {% if usuario %}
        <div class="alert alert-success text-center">
            <h2 style="margin: 0;">
                Hello, {{ usuario.nome }}!
            </h2>
            <p class="text-muted">Pleased to meet you!</p>
            <p class="small">
                ID: {{ usuario.id }} | 
                Criado em: {{ moment(usuario.criado_em).format('LLL') }}
            </p>
        </div>
        {% else %}
        <div class="alert alert-info text-center">
            <h2 style="margin: 0;">
                Hello, Stranger!
            </h2>
            <p class="text-muted">Nenhum usuário cadastrado ainda.</p>
        </div>
        {% endif %}
        
        {# Formulário #}
        <div class="panel panel-primary">
            <div class="panel-heading">
                <h3 class="panel-title">
                    <span class="glyphicon glyphicon-user"></span> 
                    What is your name?
                </h3>
            </div>
            <div class="panel-body">
                <form method="POST" action="/banco-dados">
                    <div class="form-group">
                        <input type="text" 
                               class="form-control input-lg" 
                               id="nome" 
                               name="nome" 
                               placeholder="Digite seu nome"
                               value="{{ usuario.nome if usuario else '' }}"
                               required
                               autofocus>
                    </div>
                    
                    <button type="submit" class="btn btn-primary btn-lg btn-block">
                        Submit
                    </button>
                </form>
            </div>
        </div>
        
        {# Lista de usuários #}
        <div class="panel panel-default">
            <div class="panel-heading">
                <h3 class="panel-title">
                    <span class="glyphicon glyphicon-list"></span> 
                    Usuários no Banco de Dados
                </h3>
            </div>
            <div class="panel-body">
                <p class="text-muted">
                    Total: <strong>{{ usuarios|length }}</strong> usuário(s)
                </p>
                <div class="list-group">
                    {% for u in usuarios %}
                    <div class="list-group-item">
                        <h4 class="list-group-item-heading">
                            {{ u.nome }}
                        </h4>
                        <p class="list-group-item-text text-muted small">
                            ID: {{ u.id }} | 
                            Criado: {{ moment(u.criado_em).format('LLL') }} |
                            Atualizado: {{ moment(u.atualizado_em).format('LLL') }}
                        </p>
                    </div>
                    {% else %}
                    <p class="text-center text-muted">Nenhum usuário cadastrado.</p>
                    {% endfor %}
                </div>
            </div>
        </div>
        
        {# Botão voltar #}
        <div class="text-center" style="margin-top: 20px;">
            <a href="/" class="btn btn-default">
                <span class="glyphicon glyphicon-arrow-left"></span> 
                Voltar para Home
            </a>
        </div>
    </div>
</div>
{% endblock %}
