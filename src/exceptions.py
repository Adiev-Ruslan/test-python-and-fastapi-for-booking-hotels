class NabronirovalException(Exception):
	detail = "Неожиданная ошибка"
	
	def __init__(self, *args, **kwargs):
		super().__init__(self.detail, *args, **kwargs)
		
		
class ObjectNotFoundException(NabronirovalException):
	detail = "Объект не найден"
	
	
class AllRoomsAreBookedException(NabronirovalException):
	detail = "Не осталось свободных номеров"
	

class UserAlreadyExistsException(NabronirovalException):
	status_code = 400
	detail = "Пользователь с такими данными уже зарегистрирован"
	