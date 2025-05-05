class Libro:
    def __init__(self, libro_id=None, titulo=None, subtitulo=None, isbn=None, 
                 fecha_publicacion=None, edicion=None, editorial=None, precio=None, 
                 stock=None, descripcion=None, num_paginas=None, idioma=None, 
                 calificacion=None, imagen_portada=None, formato=None):
        self.libro_id = libro_id
        self.titulo = titulo
        self.subtitulo = subtitulo
        self.isbn = isbn
        self.fecha_publicacion = fecha_publicacion
        self.edicion = edicion
        self.editorial = editorial
        self.precio = precio
        self.stock = stock
        self.descripcion = descripcion
        self.num_paginas = num_paginas
        self.idioma = idioma
        self.calificacion = calificacion
        self.imagen_portada = imagen_portada
        self.formato = formato
    
    def __str__(self):
        return f"{self.titulo} ({self.isbn}) - {self.precio}€"


class Autor:
    def __init__(self, autor_id=None, nombre=None, apellido=None, 
                 fecha_nacimiento=None, fecha_fallecimiento=None, 
                 nacionalidad=None, sitio_web=None):
        self.autor_id = autor_id
        self.nombre = nombre
        self.apellido = apellido
        self.fecha_nacimiento = fecha_nacimiento
        self.fecha_fallecimiento = fecha_fallecimiento
        self.nacionalidad = nacionalidad
        self.sitio_web = sitio_web
    
    def __str__(self):
        return f"{self.nombre} {self.apellido}"


class Categoria:
    def __init__(self, categoria_id=None, nombre=None, categoria_padre_id=None):
        self.categoria_id = categoria_id
        self.nombre = nombre
        self.categoria_padre_id = categoria_padre_id
    
    def __str__(self):
        return self.nombre


class Cliente:
    def __init__(self, cliente_id=None, nombre=None, apellido=None, email=None, 
                 telefono=None, direccion=None, ciudad=None, codigo_postal=None, 
                 pais=None, fecha_registro=None):
        self.cliente_id = cliente_id
        self.nombre = nombre
        self.apellido = apellido
        self.email = email
        self.telefono = telefono
        self.direccion = direccion
        self.ciudad = ciudad
        self.codigo_postal = codigo_postal
        self.pais = pais
        self.fecha_registro = fecha_registro
    
    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.email})"


class Venta:
    def __init__(self, venta_id=None, cliente_id=None, fecha_venta=None, 
                 total=None, metodo_pago=None, estado=None):
        self.venta_id = venta_id
        self.cliente_id = cliente_id
        self.fecha_venta = fecha_venta
        self.total = total
        self.metodo_pago = metodo_pago
        self.estado = estado
        self.detalles = []
    
    def __str__(self):
        return f"Venta #{self.venta_id} - Total: {self.total}€"


class DetalleVenta:
    def __init__(self, detalle_id=None, venta_id=None, libro_id=None, 
                 cantidad=None, precio_unitario=None, descuento=None):
        self.detalle_id = detalle_id
        self.venta_id = venta_id
        self.libro_id = libro_id
        self.cantidad = cantidad
        self.precio_unitario = precio_unitario
        self.descuento = descuento
    
    def __str__(self):
        return f"Libro ID: {self.libro_id}, Cantidad: {self.cantidad}, Precio: {self.precio_unitario}€"


class Resena:
    def __init__(self, resena_id=None, libro_id=None, cliente_id=None, 
                 calificacion=None, comentario=None, fecha_resena=None):
        self.resena_id = resena_id
        self.libro_id = libro_id
        self.cliente_id = cliente_id
        self.calificacion = calificacion
        self.comentario = comentario
        self.fecha_resena = fecha_resena
    
    def __str__(self):
        return f"Calificación: {self.calificacion}/5 - {self.comentario[:50]}..."