# core/utils.py

def safe_log(widget, text):
    """Escribe texto en un widget de texto de Tk sin bloquear."""
    try:
        widget.insert("end", text + "\n")
        widget.see("end")
    except:
        pass


def reset_progress(progressbar):
    """Reinicia una barra de progreso."""
    try:
        progressbar.config(value=0)
    except:
        pass
