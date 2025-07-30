import os

class GeneratorAppMaya:
    def __init__(self, app_name, destination=None):
        self.app_name = app_name
        self.destination = destination or os.getcwd()
        self.templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
        print(f"📁 Templates utilisés depuis : {self.templates_dir}")
        print(f"📦 Dossier de destination : {self.destination}")

    def generate(self):
        print(f"🚀 Génération de l'application Django : {self.app_name}")
        app_dir = os.path.join(self.destination, self.app_name)

        # Création des dossiers
        for subdir in ['migrations', 'models', 'views',
                       os.path.join('static', self.app_name),
                       os.path.join('templates', self.app_name)]:
            path = os.path.join(app_dir, subdir)
            os.makedirs(path, exist_ok=True)
            print(f"📂 Dossier créé : {path}")

        # Création des __init__.py
        init_files = [
            app_dir,
            os.path.join(app_dir, 'migrations'),
            os.path.join(app_dir, 'models'),
            os.path.join(app_dir, 'views'),
        ]
        for path in init_files:
            init_path = os.path.join(path, '__init__.py')
            open(init_path, 'w').close()
            print(f"📄 Fichier créé : {init_path}")

        # Copier les templates avec substitutions
        templates = {
            'admin.py.template': os.path.join(app_dir, 'admin.py'),
            'apps.py.template': os.path.join(app_dir, 'apps.py'),
            'models.py.template': os.path.join(app_dir, 'models', 'models.py'),
            'tests.py.template': os.path.join(app_dir, 'tests.py'),
            'urls.py.template': os.path.join(app_dir, 'urls.py'),
            'views.py.template': os.path.join(app_dir, 'views', 'views.py'),
        }

        for tpl_name, dest_path in templates.items():
            self._generate_from_template(tpl_name, dest_path)

        print(f"\n✅ Application '{self.app_name}' générée avec succès à l'emplacement : {app_dir}")

    def _generate_from_template(self, tpl_name, dest_path):
        tpl_path = os.path.join(self.templates_dir, 'app', tpl_name)
        if not os.path.exists(tpl_path):
            print(f"❌ Template introuvable : {tpl_path}")
            return
        with open(tpl_path, 'r') as f:
            content = f.read()
        content = content.replace('{{app_name}}', self.app_name)
        content = content.replace('{{app_name_title}}', self.app_name.title())
        with open(dest_path, 'w') as f:
            f.write(content)
        print(f"✅ Fichier généré : {dest_path}")
