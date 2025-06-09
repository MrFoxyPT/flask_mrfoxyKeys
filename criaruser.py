from app import app, db, Utilizador
with app.app_context():
    admin = Utilizador(username='FoxyAdmin', role='admin')
    admin.set_password('38pkYoutube')
    db.session.add(admin)
    db.session.commit()
    print("Conta de admin criada com sucesso!")