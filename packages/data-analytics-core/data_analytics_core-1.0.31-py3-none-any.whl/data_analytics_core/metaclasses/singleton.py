class SingletonMetaClass(type):
	"""
	This Python metaclass follows the Singleton pattern.
	In a nutshell, there can be only one instance, no matter how many times is called or re-instanced.
	"""
	_instances = {}

	def __call__(cls, *args, **kwargs):
		if cls not in cls._instances:
			cls._instances[cls] = super(SingletonMetaClass, cls).__call__(*args, **kwargs)
		return cls._instances[cls]
