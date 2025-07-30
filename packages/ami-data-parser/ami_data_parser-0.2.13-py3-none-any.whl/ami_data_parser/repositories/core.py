class BaseRepository:
    _entitie = None

    def __init__(self):
        self._objects = {}
        self._diff = []

    def all(self) -> list:
        return [self._objects.get(name) for name in self._objects]
    
    def count(self) -> int:
        return len(self._objects)
       
    def set(self, obj: object) -> None:
        items_not_changed = list(self._objects.keys())

        if type(obj) not in [list, tuple]:
            obj = [obj]
                
        for item in obj:

            if type(item) != self._entitie:
                raise ValueError()
            
            key = item.get_key()

            if key not in self._objects:
                self._diff.append((key, 'added'))
                self._objects[key] = item
            
            else:
                old_entity = self.get(key)

                if old_entity != item:
                    self._diff.append((key, 'changed'))
                    self._objects[key] = item

                    if key in items_not_changed:
                        items_not_changed.remove(key)
                
                else:
                    item.set_status_time(old_entity)
                    self._objects[key] = item
                    
                    if key in items_not_changed:
                        items_not_changed.remove(key)

        for removed_item in items_not_changed:
            del self._objects[removed_item]
            self._diff.append((removed_item, 'removed'))
    
    def exists(self, name: str) -> bool:
        return bool(name in self._objects)
    
    def delete(self, name: str) -> None:
        
        if not self.exists(name):
            raise self._entitie.DoesExists()
        
        del self._objects[name]
    
    def diff(self) -> list:
        diff = self._diff
        self._clean_diff()
        return diff
    
    def add_diff(self, data: list) -> None:

        if type(data) == list:
            if len(data) > 0:
                self._diff.extend(data)

    def get(self, name: str) -> object:
        obj = self._objects.get(name)

        if not obj:
            raise self._entitie.DoesExists(f'{name} does exists in objects repository')
        
        return obj
    
    def _clean_diff(self) -> None:
        self._diff = []