def get_branch_name(ref_data):
    """
    Повертає назву гілки з поля 'ref'.
    Наприклад, якщо ref = 'refs/heads/first', поверне 'first'.
    """
    ref = ref_data.get('ref', '')
    parts = ref.split('/')
    if len(parts) >= 3:
        return parts[-1]
    return None