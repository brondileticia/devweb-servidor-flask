"""
Rotas de listagem de e-mails enviados.
"""
from datetime import datetime
from flask import render_template, flash, redirect, url_for

from app.emails import bp
from app import db
from app.models import EmailEnviado


@bp.route('/emailsEnviados')
def emails_enviados():
    emails = EmailEnviado.query.order_by(EmailEnviado.enviado_em.desc()).all()
    total_emails = len(emails)
    total_sucesso = sum(1 for e in emails if e.sucesso)
    total_falha = total_emails - total_sucesso
    
    return render_template('emails_enviados.html',
                         emails=emails,
                         total_emails=total_emails,
                         total_sucesso=total_sucesso,
                         total_falha=total_falha,
                         current_time=datetime.utcnow(),
                         titulo='E-mails Enviados')


@bp.route('/limpar-emails')
def limpar_emails():
    EmailEnviado.query.delete()
    db.session.commit()
    flash('Histórico de e-mails limpo!', 'info')
    return redirect(url_for('emails.emails_enviados'))
