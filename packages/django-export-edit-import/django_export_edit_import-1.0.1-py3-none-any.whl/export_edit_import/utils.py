
def get_field_label_from_model_class(model_class, field_name):
    next((field.verbose_name for field in model_class._meta.get_fields() if field.name == field_name), '')