"""
Runfola, Daniel, Community Contributors, and [v4.0: Lindsey Rogers, Joshua Habib, Sidonie Horn, Sean Murphy, Dorian Miller, Hadley Day, Lydia Troup, Dominic Fornatora, Natalie Spage, Kristina Pupkiewicz, Michael Roth, Carolina Rivera, Charlie Altman, Isabel Schruer, Tara McLaughlin, Russ Biddle, Renee Ritchey, Emily Topness, James Turner, Sam Updike, Helena Buckman, Neel Simpson, Jason Lin], [v2.0: Austin Anderson, Heather Baier, Matt Crittenden, Elizabeth Dowker, Sydney Fuhrig, Seth Goodman, Grace Grimsley, Rachel Layko, Graham Melville, Maddy Mulder, Rachel Oberman, Joshua Panganiban, Andrew Peck, Leigh Seitz, Sylvia Shea, Hannah Slevin, Rebecca Yougerman, Lauren Hobbs]. "geoBoundaries: A global database of political administrative boundaries." Plos one 15, no. 4 (2020): e0231866.
"""
# Packages pour les données vectorelles
import pandas as pd
import geopandas as gpd
import geojson
from typing import *

# Packages pour les boundaries
from cartograpy.iso_code import *
from requests_cache import CachedSession
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from shapely.geometry import *

# Packages pour les données hydrographiques
import time
import requests
import zipfile
import io
import os

# Packages pour les données de la worldbank
import wbdata

# Package pour les données de OSM 
import osmnx as ox

class GeoBoundaries:
    """
    Client pour interagir avec l'API GeoBoundaries.
    Permet de récupérer les limites administratives des territoires.
    """
    
    def __init__(self, cache_expire_seconds: int = 604800):
        """
        Initialise le client GeoBoundaries.
        
        Args:
            cache_expire_seconds: Durée d'expiration du cache en secondes (défaut: 1 semaine)
        """
        self._session = CachedSession(expire_after=cache_expire_seconds)
        self._base_url = "https://www.geoboundaries.org/api/current/gbOpen"
    
    def clear_cache(self):
        """Vide le cache des requêtes."""
        self._session.cache.clear()
    
    def set_cache_expire_time(self, seconds: int):
        """
        Met à jour le temps d'expiration du cache sans vider le cache existant.
        
        Args:
            seconds: Nouvelle durée d'expiration en secondes
        """
        self._session = CachedSession(expire_after=seconds)
    
    def disable_cache(self):
        """Désactive le cache des requêtes."""
        self._session = requests
    
    def is_valid_adm(self, iso3: str, adm: str) -> bool:
        """
        Vérifie si un niveau ADM est valide pour un pays donné.
        
        Args:
            iso3: Code ISO3 du pays
            adm: Niveau administratif (ex: 'ADM0', 'ADM1', etc.)
            
        Returns:
            bool: True si le niveau ADM est valide
        """
        url = f"{self._base_url}/{iso3}/"
        html = self._session.get(url, verify=True).text
        return adm in html
    
    def _validate_adm(self, adm: Union[str, int]) -> str:
        """
        Valide et normalise un niveau ADM.
        
        Args:
            adm: Niveau administratif (int ou str)
            
        Returns:
            str: Niveau ADM validé et normalisé
            
        Raises:
            KeyError: Si le niveau ADM n'est pas valide
        """
        if isinstance(adm, int) or len(str(adm)) == 1:
            adm = f'ADM{adm}'
        
        valid_adms = [f'ADM{i}' for i in range(6)] + ['ALL']
        if str.upper(adm) in valid_adms:
            return str.upper(adm)
        
        raise KeyError(f"Niveau ADM invalide: {adm}")
    
    def _get_smallest_adm(self, iso3: str) -> str:
        """
        Trouve le plus petit niveau ADM disponible pour un pays.
        
        Args:
            iso3: Code ISO3 du pays
            
        Returns:
            str: Plus petit niveau ADM disponible
        """
        for current_adm in range(5, -1, -1):
            adm_level = f'ADM{current_adm}'
            if self.is_valid_adm(iso3, adm_level):
                print(f'Smallest ADM level found for {iso3} : {adm_level}')
                return adm_level
        
        return 'ADM0'  # Fallback
    
    def _is_valid_iso3_code(self, territory: str) -> bool:
        """
        Vérifie si un code ISO3 est valide.
        
        Args:
            territory: Code ou nom du territoire
            
        Returns:
            bool: True si le code ISO3 est valide
        """
        return str.lower(territory) in iso_codes
    
    def _get_iso3_from_name_or_iso2(self, name: str) -> str:
        """
        Convertit un nom de pays ou code ISO2 en code ISO3.
        
        Args:
            name: Nom du pays ou code ISO2
            
        Returns:
            str: Code ISO3 correspondant
            
        Raises:
            KeyError: Si le pays n'est pas trouvé
        """
        try:
            list_iso3 = self.get_iso3(name)
            if isinstance(list_iso3, str):
                return list_iso3.upper()
            # Si plusieurs pays correspondent, on retourne la liste
            elif isinstance(list_iso3, list) and len(list_iso3) >= 1:
                # Si un seul pays correspond, on retourne son code ISO3
                return list_iso3[0][1].upper()
            else:
                raise KeyError(f"{name} non trouvé")
        
        except KeyError as e:
            print(f"KeyError : Couldn't find country named {e}")
            raise KeyError(f"Pays non trouvé: {name}")
        
    def get_iso3(self, territory: str):
        """
        Récupère le code ISO3 d'un territoire.
        
        Args:
            territory: Nom du territoire ou code ISO2/ISO3
            
        Returns:
            str: Code ISO3 du territoire
            
        Raises:
            KeyError: Si le territoire n'est pas trouvé
        """
        if self._is_valid_iso3_code(territory):
            return str.upper(territory)
        else:
            list_iso3 = [(countrie_name,iso) for countrie_name, iso in countries_iso3.items() if str.lower(territory) in str.lower(countrie_name)]
            # Si aucun pays ne correspond, on retourne None
            if list_iso3 == []:
                return None
            # Si un seul pays correspond, on retourne son code ISO3
            elif len(list_iso3) == 1:
                return list_iso3[0][1].upper()
            else : # Si plusieurs pays correspondent, avec le même ISO3, on retourne le code ISO3 correspondant
                if len(set([iso for _, iso in list_iso3])) == 1:
                    return list_iso3[0][1].upper()
                else :# Sinon, on retourne la liste des pays correspondants
                    return list_iso3
    
    
    def list_countries(self) -> List[str]:
        """
        Récupère la liste des pays valides.
        
        Returns:
            List[str]: Liste des codes ISO3 des pays
        """
        return list(countries_iso3.keys())
    
    def _generate_url(self, territory: str, adm: Union[str, int]) -> str:
        """
        Génère l'URL de l'API pour un territoire et niveau ADM donnés.
        
        Args:
            territory: Nom du territoire ou code ISO
            adm: Niveau administratif
            
        Returns:
            str: URL de l'API
            
        Raises:
            KeyError: Si le territoire ou niveau ADM n'est pas valide
        """
        iso3 = (str.upper(territory) if self._is_valid_iso3_code(territory) 
                else self._get_iso3_from_name_or_iso2(territory))
        
        if adm != -1:
            adm = self._validate_adm(adm)
        else:
            adm = self._get_smallest_adm(iso3)
        
        if not self.is_valid_adm(iso3, adm):
            error_msg = f"ADM level '{adm}' doesn't exist for country '{territory}' ({iso3})"
            print(f"KeyError : {error_msg}")
            raise KeyError(error_msg)
        
        return f"{self._base_url}/{iso3}/{adm}/"
    
    def adminLevels(self):
        return """
| Niveau GeoBoundaries | Nom commun (FR)           | Nom commun (EN)       |
| -------------------- | ------------------------- | --------------------- |
| ADM0                 | Pays                      | Country               |
| ADM1                 | Région / État / Province  | State / Region        |
| ADM2                 | Département / District    | District / County     |
| ADM3                 | Sous-préfecture / Commune | Subdistrict / Commune |
| ADM4                 | Village / Localité        | Village / Locality    |
| ADM5                 | Quartier / Secteur        | Neighborhood / Sector |
        """


    def metadata(self, territory: str, adm: Union[str, int]) -> dict:
        """
        Récupère les métadonnées d'un territoire.
        
        Args:
            territory: Nom du territoire ou code ISO
            adm: Niveau administratif (utiliser 'ALL' pour tous les niveaux)
            
        Returns:
            dict: Métadonnées du territoire
        """
        url = self._generate_url(territory, adm)
        return self._session.get(url, verify=True).json()
    
    def _get_data(self, territory: str, adm: str, simplified: bool) -> str:
        """
        Récupère les données géographiques d'un territoire.
        
        Args:
            territory: Nom du territoire ou code ISO
            adm: Niveau administratif
            simplified: Si True, utilise la géométrie simplifiée
            
        Returns:
            str: Données GeoJSON sous forme de chaîne
        """
        geom_complexity = 'simplifiedGeometryGeoJSON' if simplified else 'gjDownloadURL'
        
        try:
            json_uri = self.metadata(territory, adm)[geom_complexity]
        except Exception as e:
            error_msg = f"Error while requesting geoboudaries API\n URL : {self._generate_url(territory, adm)}\n"
            print(error_msg)
            raise e
        
        return self._session.get(json_uri).text
    
    def adm(self, territories: Union[str, List[str]], adm: Union[str, int], simplified: bool = True) -> dict:
        """
        Récupère les limites administratives des territoires spécifiés.
        
        Args:
            territories: Territoire(s) à récupérer. Peut être :
                - Un string unique : "Senegal", "SEN", "เซเนกัล"
                - Une liste de strings : ["SEN", "Mali"], ["セネガル", "մալի"]
            adm: Niveau administratif :
                - 'ADM0' à 'ADM5' (si existant pour le pays)
                - int de 0 à 5
                - int -1 (retourne le plus petit niveau ADM disponible)
            simplified: Si True, utilise la géométrie simplifiée (défaut: True)
            
        Returns:
            dict: Données GeoJSON des territoires
            
        Note:
            Valeurs autorisées pour territories :
            - ISO 3166-1 (alpha2) : AFG, QAT, YEM, etc.
            - ISO 3166-1 (alpha3) : AF, QA, YE, etc.
            - Nom du pays en plusieurs langues supportées
        """
        if isinstance(territories, str):
            geo_df=gpd.GeoDataFrame.from_features(geojson.loads(self._get_data(territories, adm, simplified)))
            return geo_df
        
        # Traitement pour une liste de territoires
        geojsons_dic = {}
        for territory in territories:
            data = gpd.GeoDataFrame.from_features(geojson.loads(self._get_data(territory, adm, simplified)))
            geojsons_dic[territory]=data

        return geojsons_dic


    def continents(self,continents: Optional[Union[str, List[str]]] = None) -> gpd.GeoDataFrame:
        """
        Retourne un GeoDataFrame des continents du monde.
        
        Parameters:
        -----------
        continents : str, list of str, or None, optional
            - Si str : retourne le GeoDataFrame du continent spécifié
            - Si list : retourne le GeoDataFrame des continents dans la liste
            - Si None : retourne tous les continents
        
        Returns:
        --------
        gpd.GeoDataFrame
            GeoDataFrame contenant les géométries des continents demandés
        
        Raises:
        -------
        ValueError
            Si un continent spécifié n'existe pas dans les données
        """
        
        try:
            # Charger les données des pays du monde depuis naturalearth (URL directe)
            naturalearth_url = "https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip"
            world = gpd.read_file(naturalearth_url)
            
            # Mapping des continents pour normaliser les noms
            continent_mapping = {
                'africa': 'Africa',
                'afrique': 'Africa',
                'asia': 'Asia',
                'asie': 'Asia',
                'europe': 'Europe',
                'north america': 'North America',
                'amérique du nord': 'North America',
                'south america': 'South America',
                'amérique du sud': 'South America',
                'oceania': 'Oceania',
                'océanie': 'Oceania',
                'antarctica': 'Antarctica',
                'antarctique': 'Antarctica'
            }
            
            # Créer un GeoDataFrame des continents en dissolvant les géométries par continent
            # Le nom de la colonne peut varier selon la version des données
            continent_col = 'CONTINENT' if 'CONTINENT' in world.columns else 'continent'
            
            continents_gdf = world.dissolve(by=continent_col, as_index=False)
            continents_gdf = continents_gdf[[continent_col, 'geometry']]
            continents_gdf = continents_gdf.rename(columns={continent_col: 'continent'})
            
            # Si aucun continent spécifié, retourner tous les continents
            if continents is None:
                return continents_gdf
            
            # Si un seul continent (string)
            if isinstance(continents, str):
                continent_name = continent_mapping.get(continents.lower(), continents)
                filtered_gdf = continents_gdf[continents_gdf['continent'].str.contains(continent_name, case=False, na=False)]
                
                if filtered_gdf.empty:
                    available_continents = ', '.join(continents_gdf['continent'].unique())
                    raise ValueError(f"Continent '{continents}' non trouvé. Continents disponibles: {available_continents}")
                
                return filtered_gdf
            
            # Si une liste de continents
            elif isinstance(continents, list):
                # Normaliser les noms des continents
                normalized_continents = []
                for cont in continents:
                    normalized_name = continent_mapping.get(cont.lower(), cont)
                    normalized_continents.append(normalized_name)
                
                # Filtrer le GeoDataFrame
                mask = continents_gdf['continent'].str.lower().isin([c.lower() for c in normalized_continents])
                filtered_gdf = continents_gdf[mask]
                
                if filtered_gdf.empty:
                    available_continents = ', '.join(continents_gdf['continent'].unique())
                    raise ValueError(f"Aucun continent trouvé dans la liste. Continents disponibles: {available_continents}")
                
                # Vérifier si tous les continents demandés ont été trouvés
                found_continents = filtered_gdf['continent'].str.lower().tolist()
                missing = [c for c in continents if continent_mapping.get(c.lower(), c).lower() not in found_continents]
                
                if missing:
                    print(f"Attention: Continents non trouvés: {', '.join(missing)}")
                
                return filtered_gdf
            
            else:
                raise TypeError("Le paramètre 'continents' doit être une chaîne, une liste ou None")
        
        except Exception as e:
            print(f"Erreur lors du chargement des données: {e}")
            raise

    def list_continents_names(self):
        return {
                'africa': 'Africa',
                'afrique': 'Africa',
                'asia': 'Asia',
                'asie': 'Asia',
                'europe': 'Europe',
                'north america': 'North America',
                'amérique du nord': 'North America',
                'south america': 'South America',
                'amérique du sud': 'South America',
                'oceania': 'Oceania',
                'océanie': 'Oceania',
                'antarctica': 'Antarctica',
                'antarctique': 'Antarctica'
            }


class Geocoder:
    """
    Un objet Python pour géocoder une ou plusieurs localités en utilisant geopy
    et renvoyer les résultats dans une GeoDataFrame.

    Attributes:
        geolocator (Nominatim): L'instance du géocodeur Nominatim.
        user_agent (str): L'agent utilisateur pour les requêtes Nominatim.
        delay (float): Délai en secondes entre les requêtes pour éviter de surcharger l'API.
    """

    def __init__(self, user_agent="mon_geocoder_geopandas", delay=1.0):
        """
        Initialise l'objet Geocoder.

        Args:
            user_agent (str): Un identifiant unique pour votre application lors de l'utilisation
                              de Nominatim. Fortement recommandé.
            delay (float): Le délai en secondes entre chaque requête de géocodage.
                           Ajustez-le en fonction des limites du service.
        """
        self.user_agent = user_agent
        self.geolocator = Nominatim(user_agent=self.user_agent)
        self.delay = delay

    def _geocode_single(self, location_str):
        """
        Méthode interne pour géocoder une seule localité.

        Args:
            location_str (str): La localité à géocoder.

        Returns:
            tuple: Un tuple contenant (location_info, None) si réussi,
                   ou (None, location_str) si la localité n'est pas trouvée ou en cas d'erreur.
        """
        try:
            time.sleep(self.delay)
            location = self.geolocator.geocode(location_str)
            if location:
                return {
                    'query': location_str,
                    'address': location.address,
                    'latitude': location.latitude,
                    'longitude': location.longitude,
                    'altitude': location.altitude,
                    'raw': location.raw # Données brutes de l'API
                }, None
            else:
                return None, location_str
        except GeocoderTimedOut:
            print(f"Avertissement : Délai d'attente dépassé pour '{location_str}'.")
            return None, location_str
        except GeocoderServiceError as e:
            print(f"Erreur du service de géocodage pour '{location_str}': {e}")
            return None, location_str
        except Exception as e:
            print(f"Une erreur inattendue est survenue lors du géocodage de '{location_str}': {e}")
            return None, location_str

    def geocode(self, localities):
        """
        Géocode une ou plusieurs localités et renvoie une GeoDataFrame.

        Args:
            localities (str or list): Une seule chaîne de caractères représentant une localité,
                                      ou une liste de chaînes de caractères de localités.

        Returns:
            tuple: Un tuple contenant :
                   - geopandas.GeoDataFrame: Une GeoDataFrame avec les informations des localités trouvées
                                            et une colonne 'geometry' contenant des objets Point.
                   - list: Une liste de chaînes de caractères des localités non trouvées.
        """
        if isinstance(localities, str):
            localities = [localities]

        found_locations_data = []
        not_found_localities = []

        print(f"Début du géocodage de {len(localities)} localité(s)...")

        for locality in localities:
            location_info, not_found_locality = self._geocode_single(locality)
            if location_info:
                found_locations_data.append(location_info)
            else:
                not_found_localities.append(not_found_locality)
            
        print("Géocodage terminé.")

        # Crée une GeoDataFrame
        if found_locations_data:
            # Crée un DataFrame pandas initial
            df = pd.DataFrame(found_locations_data)
            # Crée la colonne 'geometry' à partir des longitudes et latitudes
            geometry = [Point(xy) for xy in zip(df['longitude'], df['latitude'])]
            # Convertit en GeoDataFrame, en spécifiant la colonne de géométrie et le CRS
            geodataframe = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326") # EPSG:4326 est le CRS pour les lat/lon (WGS84)
        else:
            # Crée une GeoDataFrame vide avec les colonnes attendues
            geodataframe = gpd.GeoDataFrame(columns=['query', 'address', 'latitude', 'longitude', 'altitude', 'raw', 'geometry'], geometry=[], crs="EPSG:4326")

        return geodataframe, not_found_localities


    def _reverse_geocode_single(self, coordinates_tuple):
        """
        Méthode interne pour géocoder inversement un seul ensemble de coordonnées.

        Args:
            coordinates_tuple (tuple): Un tuple de (latitude, longitude).

        Returns:
            tuple: Un tuple contenant (location_info, None) si réussi,
                   ou (None, coordinates_tuple) si l'adresse n'est pas trouvée ou en cas d'erreur.
        """
        lat, lon = coordinates_tuple
        query_str = f"{lat}, {lon}" # Pour affichage et enregistrement dans 'query'

        try:
            time.sleep(self.delay)
            location = self.geolocator.reverse(query_str)
            if location:
                return {
                    'query': query_str,
                    'address': location.address,
                    'latitude': location.latitude,
                    'longitude': location.longitude,
                    'altitude': location.altitude,
                    'raw': location.raw # Données brutes de l'API
                }, None
            else:
                return None, coordinates_tuple
        except GeocoderTimedOut:
            print(f"Avertissement : Délai d'attente dépassé pour les coordonnées '{query_str}'.")
            return None, coordinates_tuple
        except GeocoderServiceError as e:
            print(f"Erreur du service de géocodage inverse pour les coordonnées '{query_str}': {e}")
            return None, coordinates_tuple
        except Exception as e:
            print(f"Une erreur inattendue est survenue lors du géocodage inverse de '{query_str}': {e}")
            return None, coordinates_tuple


    def reverse_geocode(self, coordinates):
        """
        Géocode inversement une ou plusieurs coordonnées (coordonnées -> adresse) et renvoie une GeoDataFrame.

        Args:
            coordinates (tuple or list): Un tuple (latitude, longitude) unique,
                                         ou une liste de tuples (latitude, longitude).

        Returns:
            tuple: Un tuple contenant :
                   - geopandas.GeoDataFrame: Une GeoDataFrame avec les informations des adresses trouvées
                                            et une colonne 'geometry' contenant des objets Point.
                   - list: Une liste de tuples (latitude, longitude) des coordonnées non trouvées.
        """
        if isinstance(coordinates, tuple) and len(coordinates) == 2:
            coordinates = [coordinates] # Convertit un tuple unique en liste

        found_locations_data = []
        not_found_coordinates = []

        print(f"Début du géocodage inverse (coordonnées -> adresse) de {len(coordinates)} point(s)...")

        for coord_tuple in coordinates:
            location_info, not_found_coord = self._reverse_geocode_single(coord_tuple)
            if location_info:
                found_locations_data.append(location_info)
            else:
                not_found_coordinates.append(not_found_coord)
            
        print("Géocodage inverse (coordonnées -> adresse) terminé.")

        if found_locations_data:
            df = pd.DataFrame(found_locations_data)
            # Pour le géocodage inversé, les coordonnées d'entrée sont déjà lat/lon,
            # et les résultats retournés par geopy sont également lat/lon.
            # On utilise les latitude/longitude des résultats pour la géométrie.
            geometry = [Point(xy) for xy in zip(df['longitude'], df['latitude'])]
            geodataframe = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
        else:
            geodataframe = gpd.GeoDataFrame(columns=['query', 'address', 'latitude', 'longitude', 'altitude', 'raw', 'geometry'], geometry=[], crs="EPSG:4326")

        return geodataframe, not_found_coordinates

class WorldBank:
    def __init__(self):
        self.api_key = "_si_necessite_se_presente"
    
    def get_sources(self):
        # Renvoie une liste de sources de données disponibles sur le site de la Banque mondiale.
        return wbdata.get_sources()
    
    def get_indicators(self,source=1,query=None):
        return wbdata.get_indicators(source=source)
    
    def get_countries(self,query):
        return wbdata.get_countries(query= query)
    
    def get_data(self,indicators,country='all',**kwrargs):
        return wbdata.get_dataframe(indicators,country,**kwrargs)


class OSM :
    def __init__(self):
        self.api_key = "api_key_si_necessaire"
    
    def get_data(self,place, tags, data_type="points"):
        """
        Récupère des données OpenStreetMap pour un lieu donné (str, bbox ou GeoDataFrame)
        et des tags OSM personnalisés.
        
        Args:
            place (str, tuple, list, GeoDataFrame): Nom de la zone, bbox (minx, miny, maxx, maxy), ou GeoDataFrame polygonal.
            tags (dict): Dictionnaire des tags OSM à filtrer, ex: {"amenity": "school"}.
            data_type (str): 'points' pour POIs, 'polygons' pour surfaces, 'lines' pour lignes, 'all' pour tous types.
            
        Returns:
            geopandas.GeoDataFrame : Les objets OSM correspondant à la requête.
        """
        
        def filter_by_geometry_type(gdf, data_type):
            """Filtre le GeoDataFrame selon le type de géométrie souhaité."""
            if data_type == "points":
                return gdf[gdf.geometry.type.isin(['Point', 'MultiPoint'])]
            elif data_type == "polygons":
                return gdf[gdf.geometry.type.isin(['Polygon', 'MultiPolygon'])]
            elif data_type == "lines":
                return gdf[gdf.geometry.type.isin(['LineString', 'MultiLineString'])]
            elif data_type == "all":
                return gdf  # Retourne tous les types de géométries
            else:
                raise ValueError("data_type doit être 'points', 'polygons', 'lines' ou 'all'.")
        
        def handle_osm_request(request_func, *args, **kwargs):
            """Gère les requêtes OSM avec gestion d'erreurs."""
            try:
                gdf = request_func(*args, **kwargs)
                if gdf.empty:
                    print(f"Aucune donnée trouvée avec les tags {tags}")
                    return gpd.GeoDataFrame()
                return filter_by_geometry_type(gdf, data_type)
            except Exception as e:
                print(f"Erreur lors de la récupération des données : {e}")
                return gpd.GeoDataFrame()
        
        # Cas 1 : Nom de lieu (str)
        if isinstance(place, str):
            return handle_osm_request(ox.features_from_place, place, tags)
        
        # Cas 2 : Bounding box (tuple/list de 4 valeurs)
        elif isinstance(place, (tuple, list)) and len(place) == 4:
            minx, miny, maxx, maxy = place
            # bbox = (maxy, minx, miny, maxx)
            # OSMnx attend : north, south, east, west
            return handle_osm_request(ox.features_from_bbox, place, tags)
        
        # Cas 3 : GeoDataFrame (on prend l'enveloppe extérieure)
        elif isinstance(place, gpd.GeoDataFrame):
            try:
                # Utilise unary_union pour garder la forme exacte (sans convex_hull)
                polygon = place.union_all()
                return handle_osm_request(ox.features_from_polygon, polygon, tags)
            except Exception as e:
                print(f"Erreur lors du traitement du GeoDataFrame : {e}")
                return gpd.GeoDataFrame()
        
        else:
            raise ValueError(
                "L'argument 'place' doit être un nom de lieu (str), "
                "une bbox (tuple/list de 4 valeurs) ou un GeoDataFrame."
            )
    
    def list_tags(self,category=None, show_examples=False):
        """
        Retourne une liste de tags OSM courants, ou ceux d'une catégorie donnée.
        
        Args:
            category (str): Catégorie de tags OSM ('building', 'highway', 'amenity', 'water', 
                        'landuse', 'natural', 'leisure', 'shop', 'tourism', 'transport', 'barrier')
                        Si None, retourne toutes les catégories.
            show_examples (bool): Si True, inclut des exemples d'utilisation pour chaque catégorie.
            
        Returns:
            dict ou list: Dictionnaire de catégories avec leurs tags, ou liste des tags de la catégorie demandée.
        """
        
        # Tags organisés par catégorie avec valeurs courantes
        tags = {
            "building": {
                "description": "Bâtiments et structures",
                "tags": {
                    "building": ["yes", "house", "apartment", "commercial", "industrial", "school", "hospital", "church"],
                    "building:levels": "Nombre d'étages (valeur numérique)",
                    "building:use": ["residential", "commercial", "industrial", "retail", "office"],
                    "building:material": ["brick", "concrete", "wood", "stone", "glass"]
                },
                "example": {"building": "house", "building:levels": "2"}
            },
            
            "highway": {
                "description": "Routes, chemins et voies de circulation",
                "tags": {
                    "highway": ["motorway", "trunk", "primary", "secondary", "tertiary", "residential", "footway", "cycleway"],
                    "lanes": "Nombre de voies (valeur numérique)",
                    "surface": ["asphalt", "concrete", "paved", "unpaved", "gravel", "dirt"],
                    "maxspeed": "Vitesse maximale (ex: 50, 90, 130)",
                    "oneway": ["yes", "no", "-1"]
                },
                "example": {"highway": "primary", "lanes": "2", "maxspeed": "50"}
            },
            
            "amenity": {
                "description": "Services publics et commodités",
                "tags": {
                    "amenity": ["school", "hospital", "bank", "cafe", "restaurant", "police", "post_office", 
                            "pharmacy", "fuel", "parking", "library", "fire_station", "place_of_worship"]
                },
                "example": {"amenity": "restaurant", "cuisine": "french"}
            },
            
            "water": {
                "description": "Cours d'eau et éléments hydrauliques",
                "tags": {
                    "waterway": ["river", "stream", "canal", "drain", "ditch"],
                    "natural": ["water", "bay", "coastline"],
                    "water": ["lake", "pond", "reservoir", "river"],
                    "dam": ["yes", "weir"]
                },
                "example": {"waterway": "river", "name": "Seine"}
            },
            
            "landuse": {
                "description": "Utilisation du sol et zonage",
                "tags": {
                    "landuse": ["residential", "commercial", "industrial", "forest", "farmland", 
                            "meadow", "cemetery", "military", "recreation_ground"],
                    "natural": ["forest", "grassland", "scrub", "heath"]
                },
                "example": {"landuse": "residential", "residential": "urban"}
            },
            
            "natural": {
                "description": "Éléments naturels",
                "tags": {
                    "natural": ["tree", "peak", "water", "wood", "beach", "cliff", "hill", "valley", "cave"],
                    "tree": ["deciduous", "coniferous", "palm"],
                    "leaf_type": ["broadleaved", "needleleaved"],
                    "ele": "Altitude en mètres (valeur numérique)"
                },
                "example": {"natural": "peak", "name": "Mont Blanc", "ele": "4809"}
            },
            
            "leisure": {
                "description": "Loisirs et activités récréatives",
                "tags": {
                    "leisure": ["park", "pitch", "stadium", "swimming_pool", "playground", "golf_course", 
                            "sports_centre", "garden", "marina", "beach_resort"]
                },
                "example": {"leisure": "park", "name": "Central Park"}
            },
            
            "shop": {
                "description": "Commerces et magasins",
                "tags": {
                    "shop": ["supermarket", "bakery", "butcher", "clothes", "shoes", "books", "pharmacy", 
                            "electronics", "furniture", "car", "bicycle", "hairdresser"]
                },
                "example": {"shop": "bakery", "name": "La Boulangerie"}
            },
            
            "tourism": {
                "description": "Sites touristiques et hébergements",
                "tags": {
                    "tourism": ["hotel", "museum", "attraction", "viewpoint", "information", "camp_site", 
                            "guest_house", "hostel", "monument", "artwork"],
                    "historic": ["castle", "monument", "memorial", "archaeological_site"]
                },
                "example": {"tourism": "museum", "name": "Louvre"}
            },
            
            "transport": {
                "description": "Transport public et infrastructure",
                "tags": {
                    "railway": ["rail", "subway", "tram", "light_rail", "station", "platform"],
                    "public_transport": ["platform", "station", "stop_position"],
                    "aeroway": ["runway", "taxiway", "terminal", "gate"],
                    "route": ["bus", "tram", "subway", "train"]
                },
                "example": {"railway": "station", "name": "Gare du Nord"}
            },
            
            "barrier": {
                "description": "Barrières et obstacles",
                "tags": {
                    "barrier": ["fence", "wall", "hedge", "gate", "bollard", "kerb"],
                    "access": ["yes", "no", "private", "permissive"]
                },
                "example": {"barrier": "fence", "material": "wood"}
            }
        }
        
        def format_category_info(cat_name, cat_data):
            """Formate les informations d'une catégorie."""
            if show_examples:
                return {
                    "description": cat_data["description"],
                    "tags": cat_data["tags"],
                    "example": cat_data.get("example", {})
                }
            else:
                return list(cat_data["tags"].keys())
        
        if category is None:
            if show_examples:
                return {cat: format_category_info(cat, data) for cat, data in tags.items()}
            else:
                return {cat: list(data["tags"].keys()) for cat, data in tags.items()}
        else:
            category = category.lower()
            if category in tags:
                return format_category_info(category, tags[category])
            else:
                available_categories = list(tags.keys())
                raise ValueError(f"Catégorie '{category}' non trouvée. Catégories disponibles : {available_categories}")


    def search_tags(self,keyword):
        """
        Recherche des tags OSM contenant un mot-clé.
        
        Args:
            keyword (str): Mot-clé à rechercher dans les tags
            
        Returns:
            dict: Dictionnaire avec les catégories et tags correspondants
        """
        all_tags = self.list_tags(show_examples=True)
        results = {}
        
        keyword = keyword.lower()
        
        for category, data in all_tags.items():
            matching_tags = {}
            
            # Recherche dans les tags
            for tag_key, tag_values in data["tags"].items():
                if keyword in tag_key.lower():
                    matching_tags[tag_key] = tag_values
                elif isinstance(tag_values, list):
                    matching_values = [v for v in tag_values if keyword in v.lower()]
                    if matching_values:
                        matching_tags[tag_key] = matching_values
                elif isinstance(tag_values, str) and keyword in tag_values.lower():
                    matching_tags[tag_key] = tag_values
            
            if matching_tags:
                results[category] = {
                    "description": data["description"],
                    "matching_tags": matching_tags,
                    "example": data.get("example", {})
                }
        
        return results


    def get_common_tag_combinations(self):
        """
        Retourne des combinaisons de tags couramment utilisées ensemble.
        
        Returns:
            dict: Dictionnaire avec des exemples de requêtes courantes
        """
        return {
            "restaurants": {"amenity": "restaurant"},
            "schools": {"amenity": "school"},
            "hospitals": {"amenity": "hospital"},
            "parks": {"leisure": "park"},
            "supermarkets": {"shop": "supermarket"},
            "hotels": {"tourism": "hotel"},
            "gas_stations": {"amenity": "fuel"},
            "pharmacies": {"amenity": "pharmacy"},
            "banks": {"amenity": "bank"},
            "cafes": {"amenity": "cafe"},
            "museums": {"tourism": "museum"},
            "primary_roads": {"highway": ["primary", "trunk", "motorway"]},
            "residential_buildings": {"building": "residential"},
            "commercial_buildings": {"building": "commercial"},
            "rivers": {"waterway": "river"},
            "forests": {"landuse": "forest"},
            "beaches": {"natural": "beach"},
            "train_stations": {"railway": "station"},
            "bus_stops": {"highway": "bus_stop"},
            "parking": {"amenity": "parking"}
        }



class Hydro :
    def __init__(self):
        
        self.output_dir="hydrorivers_data"
        self.valid_regions=['af', 'as', 'au', 'eu', 'na', 'sa']


    def download(self,region: str, output_dir: str = "hydrorivers_data") -> gpd.GeoDataFrame:
        """
        Télécharge et charge les données HydroRIVERS pour une région donnée.

        Paramètres :
            region (str): Code de la région (ex: 'af', 'as', 'eu', 'na', 'sa', 'au').
            output_dir (str): Dossier local où les fichiers seront extraits.

        Retour :
            gpd.GeoDataFrame: Les données HydroRIVERS sous forme de GeoDataFrame.
        """
        self.output_dir=output_dir
        region = region.lower()
        valid_regions = self.valid_regions
        
        if region not in valid_regions:
            raise ValueError(f"Région invalide. Utilisez l’un de ces codes : {valid_regions}")
        
        url = f"https://data.hydrosheds.org/file/HydroRIVERS/HydroRIVERS_v10_{region}_shp.zip"
        region_dir = os.path.join(output_dir, region)

        if not os.path.exists(region_dir):
            os.makedirs(region_dir, exist_ok=True)
            print(f"Téléchargement des données HydroRIVERS pour la région : {region.upper()} ...")
            try:
                response = requests.get(url)
                response.raise_for_status()
                with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                    z.extractall(region_dir)
                print("Téléchargement et extraction terminés.")
            except requests.exceptions.RequestException as e:
                raise RuntimeError(f"Erreur lors du téléchargement : {e}")
        else:
            print(f"Les données pour la région {region.upper()} sont déjà présentes.")

        # Chargement du shapefile
        
        shapefile_path = os.path.join(region_dir, f'HydroRIVERS_v10_{region}_shp\HydroRIVERS_v10_{region}.shp')
        if not os.path.exists(shapefile_path):
            raise FileNotFoundError(f"Fichier {shapefile_path} introuvable après extraction.")

        rivers = gpd.read_file(shapefile_path)
        self.rivers=rivers
        return rivers
    
    def describe_variables(self) -> str:
        """
        Retourne une description textuelle des principales variables contenues dans les données HydroRIVERS.
        """
        description = """
    📘 Description des variables HydroRIVERS :
| Nom          | Signification                    | Unité / Type         |
| ------------ | -------------------------------- | -------------------- |
| `HYRIV_ID`   | ID du tronçon                    | entier               |
| `NEXT_DOWN`  | ID du tronçon aval               | entier               |
| `MAIN_RIV`   | ID du fleuve principal           | entier               |
| `LENGTH_KM`  | Longueur du segment              | km (float)           |
| `DIST_DN_KM` | Distance jusqu'à l'embouchure    | km (float)           |
| `DIST_UP_KM` | Distance depuis la source        | km (float)           |
| `CATCH_SKM`  | Surface locale du bassin versant | km² (float)          |
| `UPLAND_SKM` | Surface totale en amont          | km² (float)          |
| `ENDORHEIC`  | 1 = bassin fermé, 0 = ouvert     | booléen (int)        |
| `DIS_AV_CMS` | Débit moyen                      | m³/s (float)         |
| `ORD_STRA`   | Ordre de Strahler                | entier               |
| `ORD_CLAS`   | Classe hiérarchique simplifiée   | entier               |
| `ORD_FLOW`   | Ordre de flux                    | entier               |
| `HYBAS_L12`  | Code du bassin de niveau 12      | entier (catégorique) |
  """
        return description

