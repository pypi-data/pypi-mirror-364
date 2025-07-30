import yaml
import os
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path


class LocatorService:
    """
    Serviço simplificado para consulta de locators de Sistemas.
    
    Esta classe carrega os locators de um arquivo YAML e fornece métodos
    para consultar critérios de localização e posições dos elementos.
    """
    
    def __init__(self, yaml_file_path: str = None):
        """
        Inicializa o serviço de locators.
        
        Args:
            yaml_file_path (str, optional): Caminho para o arquivo YAML.
                                          Se None, busca 'locators.yaml' no diretório atual.
        """
        if yaml_file_path is None:
            yaml_file_path = Path(__file__).parent / "locators.yaml"
        
        self.yaml_file_path = yaml_file_path
        self._locators = self._load_locators()
    
    def _load_locators(self) -> Dict[str, Any]:
        """
        Carrega os locators do arquivo YAML.
        
        Returns:
            Dict[str, Any]: Dicionário com os locators carregados.
            
        Raises:
            FileNotFoundError: Se o arquivo YAML não for encontrado.
            yaml.YAMLError: Se houver erro na estrutura do YAML.
        """
        try:
            with open(self.yaml_file_path, 'r', encoding='utf-8') as file:
                locators = yaml.safe_load(file)
                if not locators:
                    raise ValueError("Arquivo YAML está vazio ou inválido")
                return locators
        except FileNotFoundError:
            raise FileNotFoundError(f"Arquivo de locators não encontrado: {self.yaml_file_path}")
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Erro ao carregar arquivo YAML: {e}")
    
    def reload_locators(self) -> None:
        """
        Recarrega os locators do arquivo YAML.
        Útil quando o arquivo é modificado durante a execução.
        """
        self._locators = self._load_locators()
    
    def get_locator(self, element_name: str) -> Optional[Dict[str, Any]]:
        """
        Retorna o locator completo para um elemento.
        
        Args:
            element_name (str): Nome do elemento (ex: 'main_window', 'login_username')
        
        Returns:
            Optional[Dict[str, Any]]: Dicionário com 'primary' e 'position' ou None se não encontrado.
        """
        return self._locators.get(element_name.lower())
    
    def get_primary_locator(self, element_name: str) -> Optional[Dict[str, Any]]:
        """
        Retorna apenas os critérios primários para um elemento.
        
        Args:
            element_name (str): Nome do elemento
        
        Returns:
            Optional[Dict[str, Any]]: Dicionário com os 5 critérios primários ou None se não encontrado.
        """
        locator = self.get_locator(element_name)
        return locator.get('primary') if locator else None
    
    def get_position(self, element_name: str) -> Optional[Tuple[int, int]]:
        """
        Retorna as coordenadas de posição para um elemento.
        
        Args:
            element_name (str): Nome do elemento
        
        Returns:
            Optional[Tuple[int, int]]: Tupla (coord_x, coord_y) ou None se não encontrado/definido.
        """
        locator = self.get_locator(element_name)
        if not locator or 'position' not in locator:
            return None
        
        position = locator['position']
        coord_x = position.get('coord_x')
        coord_y = position.get('coord_y')
        
        if coord_x is not None and coord_y is not None:
            return (coord_x, coord_y)
        return None
    
    def get_locator_by_attribute(self, element_name: str, attribute: str) -> Optional[Any]:
        """
        Retorna o valor de um atributo específico do locator primário.
        
        Args:
            element_name (str): Nome do elemento
            attribute (str): Nome do atributo ('control_id', 'class_name', 'auto_id', 'title_re', 'title')
        
        Returns:
            Optional[Any]: Valor do atributo ou None se não encontrado.
        """
        primary = self.get_primary_locator(element_name)
        return primary.get(attribute) if primary else None
    
    def get_non_null_attributes(self, element_name: str) -> Dict[str, Any]:
        """
        Retorna apenas os atributos não nulos do locator primário.
        
        Args:
            element_name (str): Nome do elemento
        
        Returns:
            Dict[str, Any]: Dicionário com apenas os atributos que possuem valores não nulos.
        """
        primary = self.get_primary_locator(element_name)
        if not primary:
            return {}
        
        return {key: value for key, value in primary.items() if value is not None}
    
    def list_available_elements(self) -> List[str]:
        """
        Retorna a lista de todos os elementos disponíveis.
        
        Returns:
            List[str]: Lista com os nomes dos elementos disponíveis.
        """
        return list(self._locators.keys())
    
    def element_exists(self, element_name: str) -> bool:
        """
        Verifica se um elemento existe nos locators.
        
        Args:
            element_name (str): Nome do elemento
        
        Returns:
            bool: True se o elemento existe, False caso contrário.
        """
        return element_name.lower() in self._locators
    
    def get_elements_with_position(self) -> List[str]:
        """
        Retorna lista de elementos que possuem coordenadas definidas.
        
        Returns:
            List[str]: Lista com nomes dos elementos que possuem posição definida.
        """
        elements_with_position = []
        
        for element_name in self._locators.keys():
            if self.get_position(element_name) is not None:
                elements_with_position.append(element_name)
        
        return elements_with_position
    
    def find_elements_by_attribute_value(self, attribute: str, value: Any) -> List[str]:
        """
        Busca elementos que possuem um atributo específico com determinado valor.
        
        Args:
            attribute (str): Nome do atributo
            value (Any): Valor do atributo
        
        Returns:
            List[str]: Lista com os nomes dos elementos que possuem o atributo com o valor especificado.
        """
        matching_elements = []
        
        for element_name in self._locators.keys():
            attr_value = self.get_locator_by_attribute(element_name, attribute)
            if attr_value == value:
                matching_elements.append(element_name)
        
        return matching_elements
    
    def get_complete_element_info(self, element_name: str) -> Optional[Dict[str, Any]]:
        """
        Retorna informações completas de um elemento (locators + posição formatados).
        
        Args:
            element_name (str): Nome do elemento
        
        Returns:
            Optional[Dict[str, Any]]: Dicionário com informações completas ou None se não encontrado.
        """
        locator = self.get_locator(element_name)
        if not locator:
            return None
        
        info = {
            'element_name': element_name,
            'primary_attributes': self.get_non_null_attributes(element_name),
            'position': self.get_position(element_name),
            'has_position': self.get_position(element_name) is not None
        }
        
        return info
    
    def validate_locator_structure(self) -> Dict[str, List[str]]:
        """
        Valida a estrutura dos locators carregados.
        
        Returns:
            Dict[str, List[str]]: Dicionário com 'valid' e 'invalid' contendo listas de elementos.
        """
        valid_elements = []
        invalid_elements = []
        required_primary_keys = {'control_id', 'class_name', 'auto_id', 'title_re', 'title'}
        required_position_keys = {'coord_x', 'coord_y'}
        
        for element_name, locator_data in self._locators.items():
            is_valid = True
            
            # Verifica estrutura primary
            if not isinstance(locator_data, dict) or 'primary' not in locator_data:
                is_valid = False
            else:
                primary = locator_data['primary']
                if not isinstance(primary, dict) or not required_primary_keys.issubset(primary.keys()):
                    is_valid = False
            
            # Verifica estrutura position
            if 'position' not in locator_data:
                is_valid = False
            else:
                position = locator_data['position']
                if not isinstance(position, dict) or not required_position_keys.issubset(position.keys()):
                    is_valid = False
            
            if is_valid:
                valid_elements.append(element_name)
            else:
                invalid_elements.append(element_name)
        
        return {
            'valid': valid_elements,
            'invalid': invalid_elements
        }


# Exemplo de uso
if __name__ == "__main__":
    # Instancia o serviço
    locator_service = LocatorService()
    
    print("=== Elementos disponíveis ===")
    print(locator_service.list_available_elements())
    
    print("\n=== Informações completas do campo de usuário ===")
    username_info = locator_service.get_complete_element_info('login_username')
    print(username_info)
    
    print("\n=== Apenas atributos não nulos do botão de login ===")
    login_btn_attrs = locator_service.get_non_null_attributes('login_button')
    print(login_btn_attrs)
    
    print("\n=== Posição do campo de senha ===")
    password_position = locator_service.get_position('login_password')
    print(f"Coordenadas: {password_position}")
    
    print("\n=== Elementos com posição definida ===")
    elements_with_pos = locator_service.get_elements_with_position()
    print(elements_with_pos)
    
    print("\n=== Elementos com class_name 'TButton' ===")
    tbutton_elements = locator_service.find_elements_by_attribute_value('class_name', 'TButton')
    print(tbutton_elements)
    
    print("\n=== Validação da estrutura ===")
    validation = locator_service.validate_locator_structure()
    print(f"Válidos: {validation['valid']}")
    print(f"Inválidos: {validation['invalid']}")