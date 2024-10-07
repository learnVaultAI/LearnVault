from enhanced_app.models.roadmap import Category

def create_category(name, description, is_core=False, parent_id=None, icon_url=None):
    return Category.create(name, description, is_core, parent_id, icon_url)

def get_all_categories():
    return Category.get_all_categories()

def get_core_categories():
    return Category.get_core_categories()

def update_category(category_id, **kwargs):
    Category.update(category_id, **kwargs)

def delete_category(category_id):
    Category.delete(category_id)

def get_category_by_id(category_id):
    return Category.get_by_id(category_id)
