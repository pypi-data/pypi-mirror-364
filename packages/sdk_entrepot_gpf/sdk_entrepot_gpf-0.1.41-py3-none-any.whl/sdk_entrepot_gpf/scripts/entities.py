from __future__ import annotations  # utile pour le typage "argparse._SubParsersAction[argparse.ArgumentParser]"

import argparse
import re
from typing import Callable, List, Optional, Sequence
from shapely.geometry import shape  # type:ignore
from shapely.wkt import dumps  # type:ignore
from tabulate import tabulate

from sdk_entrepot_gpf.Errors import GpfSdkError
from sdk_entrepot_gpf.io.Config import Config
from sdk_entrepot_gpf.store.interface.LogsInterface import LogsInterface
from sdk_entrepot_gpf.workflow.action.DeleteAction import DeleteAction
from sdk_entrepot_gpf.workflow.action.UploadAction import UploadAction
from sdk_entrepot_gpf.store import TYPE__ENTITY
from sdk_entrepot_gpf.store.Annexe import Annexe
from sdk_entrepot_gpf.store.Check import Check
from sdk_entrepot_gpf.store.CheckExecution import CheckExecution
from sdk_entrepot_gpf.store.Configuration import Configuration
from sdk_entrepot_gpf.store.Datastore import Datastore
from sdk_entrepot_gpf.store.Endpoint import Endpoint
from sdk_entrepot_gpf.store.Key import Key
from sdk_entrepot_gpf.store.Metadata import Metadata
from sdk_entrepot_gpf.store.Offering import Offering
from sdk_entrepot_gpf.store.Permission import Permission
from sdk_entrepot_gpf.store.Processing import Processing
from sdk_entrepot_gpf.store.Static import Static
from sdk_entrepot_gpf.store.StoredData import StoredData
from sdk_entrepot_gpf.store.Tms import Tms
from sdk_entrepot_gpf.store.Upload import Upload
from sdk_entrepot_gpf.store.ProcessingExecution import ProcessingExecution
from sdk_entrepot_gpf.store.StoreEntity import StoreEntity
from sdk_entrepot_gpf.store.interface.TagInterface import TagInterface

from sdk_entrepot_gpf.scripts.utils import Utils


class Entities:
    """Classe pour manipuler les entités en cas d'utilisation cli."""

    ENTITIES = [
        Annexe,
        Check,
        CheckExecution,
        Configuration,
        Datastore,
        Endpoint,
        Key,
        Metadata,
        Offering,
        Permission,
        Processing,
        ProcessingExecution,
        Static,
        StoredData,
        Tms,
        Upload,
    ]

    def __init__(self, datastore: Optional[str], entity_type: str, idu: Optional[str], args: argparse.Namespace) -> None:  # pylint: disable=too-many-branches
        """Si un id est précisé, on récupère l'entité et on fait d'éventuelles actions.
        Sinon on liste les entités avec éventuellement des filtres.

        Args:
            datastore (Optional[str], optional): datastore à considérer
            entity_type (str): type d'entité à gérer
            id (Optional[str]): id de l'entité à manipuler
            args (argparse.Namespace): reste des paramètres
        """

        self.datastore = datastore
        self.entity_type = entity_type
        self.entity_class = TYPE__ENTITY[entity_type]
        self.idu = idu
        self.args = args

        if self.idu is not None:
            o_entity = self.entity_class.api_get(self.idu, datastore=self.datastore)
            # On fait les actions
            if self.action(o_entity):  # si ça retourne True
                # On affiche l'entité
                Config().om.info(f"Affichage de l'entité {o_entity} :", green_colored=True)
                Entities.print_entity(o_entity, "")
        elif getattr(self.args, "publish_by_label", False) is True:
            Entities.action_annexe_publish_by_labels(self.args.publish_by_label.split(","), datastore=self.datastore)
        elif getattr(self.args, "unpublish_by_label", False) is True:
            Entities.action_annexe_unpublish_by_labels(self.args.unpublish_by_label.split(","), datastore=self.datastore)
        else:
            d_infos_filter = StoreEntity.filter_dict_from_str(self.args.infos)
            if getattr(self.args, "tags", None) is not None:
                d_tags_filter = StoreEntity.filter_dict_from_str(self.args.tags)
            else:
                d_tags_filter = None
            l_entities = self.entity_class.api_list(infos_filter=d_infos_filter, tags_filter=d_tags_filter, page=getattr(self.args, "page", None), datastore=self.datastore)
            Config().om.info(f"Affichage de {len(l_entities)} {self.entity_class.entity_titles()} :", green_colored=True)
            Entities.tabulate_entities(self.entity_type, l_entities, sep="")

    @staticmethod
    def tabulate_entities(entity_type: str, entities: Sequence[StoreEntity], sep: str = "\n") -> None:
        """Affiche la liste d'entités sous forme de tableau.

        Args:
            entity_type (str): type des entités (pour récupérer les colonnes en config)
            entities (Sequence[StoreEntity]): entités
            sep (str, optional): séparateur à la fin du tableau. Defaults to "\n".
        """
        l_props = str(Config().get("cli", f"list_{entity_type}", "_id,name"))
        print(tabulate([o_e.get_store_properties(l_props.split(",")) for o_e in entities], headers="keys") + sep)

    @staticmethod
    def print_entity(o_entity: StoreEntity, extent: str = "") -> None:
        """Affiche l'entité avec la possibilité de choisir l'affichage du extent

        Args:
            extent (str): Type de l'affichage du extent
        """
        # Gestion de l'affichage de l'emprise
        b_extent_hidden = False
        if o_entity.get("extent") is not None:
            if extent == "geojson":  # Si geojson, on ne fait rien
                pass
            elif extent == "wkt":  # si wkt on converti
                o_entity.set_key("extent", dumps(shape(o_entity.get("extent")["geometry"])))
            # elif extent == "show": # si shown on l'affiche
            #     coordinates = o_entity.get("extent")["geometry"]["coordinates"]
            #     m = folium.Map(location = coordinates[0], zoom_start=10)
            #     folium.Polygon(coordinates, color="blue", fill= True).add_to(m)
            else:  # sinon, on la retire
                o_entity.delete_key("extent")
                b_extent_hidden = True

        # Affichage entité
        print(o_entity.to_json(indent=3))

        # Affichage remarques
        if b_extent_hidden:
            Config().om.info("Emprise masquée, utilisez la commande --extent pour l'afficher.")

    def action(self, o_entity: StoreEntity) -> bool:  # pylint:disable=too-many-branches,too-many-statements,too-many-return-statements
        """Traite les actions s'il y a lieu. Renvoie true si on doit afficher l'entité.

        Args:
            o_entity (StoreEntity): entité à traiter

        Returns:
            bool: true si on doit afficher l'entité
        """
        b_return = True
        # Gestion des actions communes
        if getattr(self.args, "delete", False) is True:
            Entities.action_entity_delete(o_entity, self.args.cascade, self.args.force, self.datastore)
            b_return = False

        if getattr(self.args, "extent", None) is not None:
            Entities.print_entity(o_entity, self.args.extent)
            b_return = False

        # Gestion des actions liées aux Livraisons
        if getattr(self.args, "open", False) is True:
            assert isinstance(o_entity, Upload)
            Entities.action_upload_open(o_entity)
            b_return = False
        if getattr(self.args, "checks", False) is True:
            assert isinstance(o_entity, Upload)
            Entities.action_upload_checks(o_entity)
            b_return = False
        if getattr(self.args, "delete_files", None) is not None:
            assert isinstance(o_entity, Upload)
            Entities.action_upload_delete_files(o_entity, self.args.delete_files)
            b_return = False
        if getattr(self.args, "logs", None) is not None:
            assert isinstance(o_entity, LogsInterface)
            self.action_execution_logs(o_entity, self.args.logs)
            b_return = False
        if getattr(self.args, "delete_failed_files", False) is True:
            assert isinstance(o_entity, Upload)
            Entities.action_upload_delete_failed_files(o_entity)
            b_return = False
        if getattr(self.args, "close", False) is True:
            assert isinstance(o_entity, Upload)
            Entities.action_upload_close(o_entity, self.args.mode_cartes)
            b_return = False
        if getattr(self.args, "relative_entities", False) is True:
            assert isinstance(o_entity, StoreEntity)
            Entities.action_relative_entities(o_entity)
            b_return = False

        # Gestion des actions liées aux Annexes
        if getattr(self.args, "publish", False) is True:
            assert isinstance(o_entity, Annexe)
            Entities.action_annexe_publish(o_entity)
            b_return = False
        if getattr(self.args, "unpublish", False) is True:
            assert isinstance(o_entity, Annexe)
            Entities.action_annexe_unpublish(o_entity)
            b_return = False

        # Gestion des actions liées aux Exécution de traitement
        if getattr(self.args, "abort", False):
            assert isinstance(o_entity, ProcessingExecution)
            Entities.action_execution_abort(o_entity)
            b_return = False

        # Gestion des actions liées aux Points d'accès
        if getattr(self.args, "publish_metadata", None) is not None:
            assert isinstance(o_entity, Endpoint)
            Entities.action_endpoint_publish_metadata(o_entity, self.args.publish_metadata, self.args.datastore)
            b_return = False
        if getattr(self.args, "unpublish_metadata", None) is not None:
            assert isinstance(o_entity, Endpoint)
            Entities.action_endpoint_unpublish_metadata(o_entity, self.args.unpublish_metadata, self.args.datastore)
            b_return = False

        return b_return

    @staticmethod
    def action_entity_delete(entity: StoreEntity, cascade: bool, force: bool, datastore: Optional[str]) -> None:
        """Suppression de l'entité indiquée, éventuellement en cascade.

        Args:
            entity (StoreEntity): entité à gérer
            cascade (bool): est-ce qu'il faut supprimer en cascade
            force (bool): est-ce qu'il faut demander confirmation
            datastore (Optional[str]): datastore à considérer
        """
        # création du workflow pour l'action de suppression
        d_action = {
            "type": "delete-entity",
            "entity_type": entity.entity_name(),
            "entity_id": entity.id,
            "cascade": cascade,
            "confirm": not force,
        }
        o_action_delete = DeleteAction("contexte", d_action)
        o_action_delete.run(datastore)

    @staticmethod
    def action_execution_abort(entity: ProcessingExecution) -> None:
        """Arrêt de l'execution de traitement.

        Args:
            entity (ProcessingExecution): entité à gérer
        """
        s_output = entity["output"].get("upload", entity["output"].get("stored_data", {"name": "indéfini"}))["name"]
        Config().om.info(f"Annulation de l'exécution de traitement {entity['processing']['name']} => {s_output}...")
        entity.api_abort()
        Config().om.info("Annulation effectuée avec succès.", green_colored=True)

    @staticmethod
    def action_endpoint_publish_metadata(endpoint: Endpoint, l_metadata: List[str], datastore: Optional[str]) -> None:
        Metadata.publish(l_metadata, endpoint.id, datastore)
        Config().om.info(f"Les métadonnées ont été publiées sur le endpoint {endpoint}.")

    @staticmethod
    def action_endpoint_unpublish_metadata(endpoint: Endpoint, l_metadata: List[str], datastore: Optional[str]) -> None:
        Metadata.unpublish(l_metadata, endpoint.id, datastore)
        Config().om.info(f"Les métadonnées ont été dépubliées du endpoint {endpoint}.")

    @staticmethod
    def action_upload_open(upload: Upload) -> None:
        """réouverture d'une livraison

        Args:
            upload (Upload): livraison à ouvrir

        Raises:
            GpfSdkError: impossible d'ouvrir la livraison
        """
        if upload.is_open():
            Config().om.warning(f"La livraison {upload} est déjà ouverte.")
            return
        if upload["status"] in [Upload.STATUS_CLOSED, Upload.STATUS_UNSTABLE]:
            upload.api_open()
            Config().om.info(f"La livraison {upload} vient d'être rouverte.", green_colored=True)
            return
        raise GpfSdkError(f"La livraison {upload} n'est pas dans un état permettant de d'ouvrir la livraison ({upload['status']}).")

    @staticmethod
    def action_upload_close(
        upload: Upload,
        mode_cartes: bool,
        callback: Optional[Callable[[str], None]] = print,
        ctrl_c_action: Optional[Callable[[], bool]] = Utils.ctrl_c_upload,
    ) -> None:
        """fermeture d'une livraison

        Args:
            upload (Upload): livraison à fermer
            mode_cartes (Optional[bool]): Si le mode carte est activé
            callback (Optional[Callable[[str], None]]): fonction de callback à exécuter avec le message de suivi.
            ctrl_c_action (Optional[Callable[[], bool]]): gestion du ctrl-C
        Raises:
            GpfSdkError: impossible de fermer la livraison
        """
        # si ouverte : on ferme puis monitoring
        if upload.is_open():
            # fermeture de l'upload
            upload.api_close()
            Config().om.info(f"La livraison {upload} vient d'être fermée.", green_colored=True)
            # monitoring des tests :
            Utils.monitoring_upload(
                upload,
                "Livraison {upload} fermée avec succès.",
                "Livraison {upload} fermée en erreur !",
                callback,
                ctrl_c_action,
                mode_cartes,
            )
            return
        # si STATUS_CHECKING : monitoring
        if upload["status"] == Upload.STATUS_CHECKING:
            Config().om.info(f"La livraison {upload} est fermée, les tests sont en cours.")
            Utils.monitoring_upload(
                upload,
                "Livraison {upload} fermée avec succès.",
                "Livraison {upload} fermée en erreur !",
                callback,
                ctrl_c_action,
                mode_cartes,
            )
            return
        # si ferme OK ou KO : warning
        if upload["status"] in [Upload.STATUS_CLOSED, Upload.STATUS_UNSTABLE]:
            Config().om.warning(f"La livraison {upload} est déjà fermée, statut : {upload['status']}")
            return
        # autre : action impossible
        raise GpfSdkError(f"La livraison {upload} n'est pas dans un état permettant d'être fermée ({upload['status']}).")

    @staticmethod
    def action_upload_checks(upload: Upload) -> None:
        """Affiche les infos sur une livraison

        Args:
            upload (Upload): livraison à vérifier
        """
        d_checks = upload.api_list_checks()
        Config().om.info(f"Bilan des vérifications de la livraison {upload} :")
        if len(d_checks["passed"]) != 0:
            Config().om.info(f"\t * {len(d_checks['passed'])} vérifications passées avec succès :")
            for d_verification in d_checks["passed"]:
                Config().om.info(f"\t\t - {d_verification['check']['name']} ({d_verification['_id']})")
        if len(d_checks["asked"] + d_checks["in_progress"]) != 0:
            Config().om.warning(f"* {len(d_checks['asked']) + len(d_checks['in_progress'])} vérifications en cours ou en attente :", yellow_colored=True)
            for d_verification in d_checks["asked"] + d_checks["in_progress"]:
                s_name = "asked" if d_verification in d_checks["asked"] else "in_progress"
                Config().om.info(f"\t\t - {s_name} {d_verification['check']['name']} ({d_verification['_id']})")
        if len(d_checks["failed"]) != 0:
            Config().om.warning(f"* {len(d_checks['failed'])} vérifications échouées :", yellow_colored=True)
            for d_verification in d_checks["failed"]:
                o_check = CheckExecution(d_verification, datastore=upload.datastore)
                l_logs = o_check.api_logs_filter(str_filter="ERROR").logs
                if l_logs:
                    s_logs = "\n" + "\n".join(l_logs)
                else:
                    s_logs = "\nPas de log contenant 'ERROR', regardez le détail des logs avec la commande 'logs'."
                Config().om.info(f"\t\t - {d_verification['check']['name']} ({d_verification['_id']}) - extrait des logs :{s_logs}")

    @staticmethod
    def action_upload_delete_files(upload: Upload, delete_files: List[str]) -> None:
        """Supprime les fichiers distants indiqués. La livraison n'est ni ouverte ni fermée,
        mais l'utilisateur peut combiner les actions si besoin.

        Args:
            upload (Upload): livraison à considérer
            delete_files (List[str]): liste des fichiers distants à supprimer.
        """
        if not upload.is_open():
            raise GpfSdkError("La livraison est actuellement fermée, ajoutez '--open' à la commande si vous souhaitez qu'elle soit rouverte.")
        Config().om.info(f"Suppression de {len(delete_files)} fichiers téléversés sur la livraison {upload['name']} :")
        for s_file in delete_files:
            if s_file.endswith(".md5"):
                Config().om.info(f"\t - suppression du fichier de clefs '{s_file}'")
                upload.api_delete_data_file(s_file)
            else:
                Config().om.info(f"\t - suppression du fichier de données '{s_file}'")
                upload.api_delete_md5_file(s_file)
        Config().om.info(f"Suppression de {len(delete_files)} fichiers effectuée avec succès.", green_colored=True)

    @staticmethod
    def action_upload_delete_failed_files(upload: Upload) -> None:
        """Liste et propose de supprimer les fichiers indiqués comme invalides par les vérifications.

        Args:
            upload (Upload): livraison concernée
            datastore (Optional[str]): datastore concerné
        """
        Config().om.info(f"Suppression des fichiers mal téléversés sur la livraison {upload['name']} :")
        Config().om.info("Listing des fichiers à supprimer...")
        o_regex = re.compile(r"\((.*?)\)")
        l_accepted_check_names = ["Vérification standard"]
        l_files = []
        l_check_execs = upload.api_list_checks()
        # On cherche des fichiers à supprimer uniquement pour la Vérification standard si elle est 'failed'
        for d_check_exec in l_check_execs["failed"]:
            if d_check_exec["check"]["name"] in l_accepted_check_names:
                o_check_exec = CheckExecution(d_check_exec, datastore=upload.datastore)
                l_lines = o_check_exec.api_logs_filter(str_filter="ERROR").logs
                for s_line in l_lines:
                    o_match = o_regex.search(s_line)
                    if o_match:
                        s_file = o_match.group(1)
                        l_files.append(s_file)
        if not l_files:
            Config().om.warning("Aucun fichier incorrect à supprimer.")
        else:
            s_files = "\n    * " + "\n    * ".join(l_files)
            Config().om.info(f"{len(l_files)} fichiers incorrects à supprimer :{s_files}")
            Config().om.warning("Voulez-vous effectuer la suppression ? (oui/NON)")
            s_rep = input()
            # si la réponse ne correspond pas à oui on sort
            if s_rep.lower() not in ["oui", "o", "yes", "y"]:
                Config().om.info("Suppression annulée.", green_colored=True)
                return
            # ouverture de la livraison
            upload.api_open()
            # Suppression des fichiers
            for s_file in l_files:
                upload.api_delete_data_file(s_file)
            Config().om.info(f"Suppression des {len(l_files)} fichiers effectuées avec succès.", green_colored=True)

    @staticmethod
    def action_execution_logs(execution: LogsInterface, filters: str) -> None:
        """Applique les filtres au logs de l'exécution
        Args:
            execution: L'exécution où vont être appliqué les filtres.
            filters: Les différents filtres qui seront appliqués sur l'exécution.
        """
        if filters == "":
            filters = "-1:0/25"
        o_pattern = r"(\-?\d+)(?::(\-?\d+))?(?:/(\-?\d+))?\|?(\w*)?"
        o_match = re.match(o_pattern, filters)
        if o_match is None:
            Config().om.info(f"Impossible de parser {filters}, utilisation de -1:0/25.")
            i_firstpage, i_lastpage, i_lineperpage, s_filter = "-1", "0", "25", ""
        else:
            i_firstpage, i_lastpage, i_lineperpage, s_filter = o_match.groups()
        if i_lastpage is None:
            i_lastpage = 0
        if i_lineperpage is None:
            i_lineperpage = 2000
        if s_filter is None:
            s_filter = ""
        Config().om.info(f"Récupération des logs de l'{execution.entity_title()} {execution.id} ({i_firstpage}:{i_lastpage}/{i_lineperpage}|{s_filter})...")
        l_lines = execution.api_logs_filter(int(i_firstpage), int(i_lastpage), int(i_lineperpage), s_filter).logs
        Config().om.info(f"{len(l_lines)} logs récupérés :\n" + "\n".join(l_lines))

    @staticmethod
    def action_relative_entities(entity: StoreEntity) -> None:  # pylint:disable=too-many-branches,too-many-statements
        """Affiche les entités liées a l'entité indiquée.

        Args:
            entity (StoreEntity): entité indiquée
        """
        if isinstance(entity, Upload):
            Config().om.info(f"Affichage des entités liées à la livraison {entity['name']} :", green_colored=True)

            l_pe_avals = ProcessingExecution.api_list(infos_filter={"input_upload": entity.id})
            if len(l_pe_avals) > 0:
                Config().om.info(f"\t * Affichage des {len(l_pe_avals)} exécutions de traitements en aval :")
                Entities.tabulate_entities(ProcessingExecution.entity_name(), l_pe_avals)
            else:
                Config().om.info("\t * Aucune exécution de traitements en aval.\n")

            l_pe_amonts = ProcessingExecution.api_list(infos_filter={"output_upload": entity.id})
            if l_pe_amonts:
                Config().om.info(f"\t * Affichage des {len(l_pe_amonts)} exécutions de traitements en amont :")
                Entities.tabulate_entities(ProcessingExecution.entity_name(), l_pe_amonts)
            else:
                Config().om.info("\t * Aucune exécution de traitements en amont.\n")

            d_checks = entity.api_list_checks()
            l_temp = d_checks["passed"] + d_checks["asked"] + d_checks["in_progress"] + d_checks["failed"]
            l_checks = [CheckExecution(d_check_exec, datastore=entity.datastore) for d_check_exec in l_temp]
            if len(l_checks) > 0:
                Config().om.info(f"\t * Affichage des {len(l_checks)} exécutions de vérification :")
                Entities.tabulate_entities(CheckExecution.entity_name(), l_checks)
            else:
                Config().om.info("\t * Aucune vérification.\n")

        if isinstance(entity, StoredData):
            Config().om.info(f"Affichage des entités liées à la donnée stockée {entity['name']} :", green_colored=True)

            l_configurations = Configuration.api_list(infos_filter={"stored_data": entity.id})
            if len(l_configurations) > 0:
                Config().om.info(f"\t * Affichage des {len(l_configurations)} configurations liées :")
                Entities.tabulate_entities(Configuration.entity_name(), l_configurations)
            else:
                Config().om.info("\t * Aucune configuration.\n")

            l_offerings = Offering.api_list(infos_filter={"stored_data": entity.id})
            if len(l_offerings) > 0:
                Config().om.info(f"\t * Affichage des {len(l_offerings)} offres liées :")
                Entities.tabulate_entities(Offering.entity_name(), l_offerings)
            else:
                Config().om.info("\t * Aucune offre.\n")

            l_pe_avals = ProcessingExecution.api_list(infos_filter={"input_stored_data": entity.id})
            if len(l_pe_avals) > 0:
                Config().om.info(f"\t * Affichage des {len(l_pe_avals)} exécutions de traitements en aval :")
                Entities.tabulate_entities(ProcessingExecution.entity_name(), l_pe_avals)
            else:
                Config().om.info("\t * Aucune exécution de traitements en aval.\n")

            l_pe_amonts = ProcessingExecution.api_list(infos_filter={"output_stored_data": entity.id})
            if len(l_pe_amonts) > 0:
                Config().om.info(f"\t * Affichage des {len(l_pe_amonts)} exécutions de traitements en amont :")
                Entities.tabulate_entities(ProcessingExecution.entity_name(), l_pe_amonts)
            else:
                Config().om.info("\t * Aucune exécution de traitements en amont.\n")

        if isinstance(entity, CheckExecution):
            Config().om.info(f"Affichage des entités liées à l'exécution de vérification {entity['name']} :", green_colored=True)
            Config().om.info(f"\t * Livraison : {entity}")
            Config().om.info(f"\t * Vérification : {entity}")

        if isinstance(entity, ProcessingExecution):
            s_output = entity["output"].get("upload", entity["output"].get("stored_data", {"name": ""}))["name"]
            Config().om.info(f"Affichage des entités liées à l'exécution de traitement {entity['processing']} => {s_output} :", green_colored=True)
            l_in_uploads = [Upload(x, datastore=entity.datastore) for x in entity["inputs"].get("upload", [])]
            l_in_stored_data = [StoredData(x, datastore=entity.datastore) for x in entity["inputs"].get("stored_data", [])]
            Config().om.info("\t * Entrée(s) :")
            if l_in_uploads:
                StoreEntity.list_api_update(l_in_uploads)
                Config().om.info("\t\t - Livraison(s) :")
                Entities.tabulate_entities("upload", l_in_uploads, sep="")
            if l_in_stored_data:
                StoreEntity.list_api_update(l_in_stored_data)
                Config().om.info("\t\t - Données stockées(s) :")
                Entities.tabulate_entities("stored_data", l_in_stored_data, sep="")
            print("\n")
            if "upload" in entity["output"]:
                o_out_upload = Upload(entity["output"]["upload"], datastore=entity.datastore)
                o_out_upload.api_update()
                Config().om.info("\t * Sortie (livraison) :")
                Entities.tabulate_entities("update", [o_out_upload])
            elif "stored_data" in entity["output"]:
                o_out_stored_data = StoredData(entity["output"]["stored_data"], datastore=entity.datastore)
                o_out_stored_data.api_update()
                Config().om.info("\t * Sortie (donnée stockée) :")
                Entities.tabulate_entities("stored_data", [o_out_stored_data])
            else:
                Config().om.info(f"\t * Sortie : {entity['output']}")

        if isinstance(entity, Configuration):
            Config().om.info(f"Affichage des entités liées à la configuration {entity['name']} :", green_colored=True)
            l_stored_datas = [StoredData.api_get(x["stored_data"], datastore=entity.datastore) for x in entity["type_infos"]["used_data"]]
            if l_stored_datas:
                Config().om.info(f"\t * Affichage des {len(l_stored_datas)} données stockées liées :")
                Entities.tabulate_entities("stored_data", l_stored_datas)
                l_offerings = entity.api_list_offerings()
            else:
                Config().om.info("\t * Aucune donnée stockée liée.\n")

            if len(l_offerings) > 0:
                Config().om.info(f"\t * Affichage des {len(l_offerings)} offres liées :")
                Entities.tabulate_entities(Offering.entity_name(), l_offerings)
            else:
                Config().om.info("\t * Aucune offre liée.\n")

        if isinstance(entity, Offering):
            Config().om.info(f"Affichage des entités liées à l'offre {entity['endpoint']['name']} - {entity['layer_name']} :", green_colored=True)
            Config().om.info("\t * Point d'accès :")
            o_endpoint = Endpoint(entity["endpoint"], datastore=entity.datastore)
            Entities.tabulate_entities("endpoint", [o_endpoint])
            Config().om.info("\t * Configuration :")
            o_configuration = Configuration.api_get(entity["configuration"]["_id"], datastore=entity.datastore)
            Entities.tabulate_entities("configuration", [o_configuration])

    @staticmethod
    def action_annexe_publish(annexe: Annexe) -> None:
        """Publie l'annexe indiquée.

        Args:
            annexe (Annexe): annexe à publier
        """
        if annexe["published"]:
            Config().om.info(f"L'annexe ({annexe}) est déjà publiée.")
            return
        # modification de la publication
        annexe.api_partial_edit({"published": str(True)})
        Config().om.info(f"L'annexe ({annexe}) a été publiée.")

    @staticmethod
    def action_annexe_unpublish(annexe: Annexe) -> None:
        """Dé-publie l'annexe indiquée.

        Args:
            annexe (Annexe): annexe à dépublier.
        """
        if not annexe["published"]:
            Config().om.info(f"L'annexe ({annexe}) n'est pas publiée.")
            return
        # modification de la publication
        annexe.api_partial_edit({"published": str(False)})
        Config().om.info(f"L'annexe ({annexe}) a été dépubliée.")

    @staticmethod
    def action_annexe_publish_by_labels(l_labels: List[str], datastore: Optional[str]) -> None:
        i_nb = Annexe.publish_by_label(l_labels, datastore=datastore)
        Config().om.info(f"{i_nb} annexe(s) ont été publiée(s).")

    @staticmethod
    def action_annexe_unpublish_by_labels(l_labels: List[str], datastore: Optional[str]) -> None:
        i_nb = Annexe.unpublish_by_label(l_labels, datastore=datastore)
        Config().om.info(f"{i_nb} annexe(s) ont été dépubliée(s).")

    @staticmethod
    def complete_parser_entities(o_sub_parsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:  # pylint: disable=too-many-statements,too-many-branches
        """Complète le parser avec les sous-parsers pour chaque entité."""
        # Pour chaque entité
        for o_entity in Entities.ENTITIES:
            # On crée le parseur
            o_sub_parser = o_sub_parsers.add_parser(
                f"{o_entity.entity_name()}",
                help=f"Gestion des {o_entity.entity_titles()}",
                formatter_class=argparse.RawTextHelpFormatter,
            )
            # Puis on génère la doc en ajoutant les paramètres
            l_epilog = []
            l_epilog.append("""Types de lancement :""")
            # Id
            o_sub_parser.add_argument("id", type=str, nargs="?", default=None, help="Id de l'entité à afficher ou à utiliser pour lancer les actions")
            # Filtres
            o_sub_parser.add_argument("--infos", "-i", type=str, default=None, help=f"Filtrer les {o_entity.entity_titles()} selon les infos")
            o_sub_parser.add_argument("--page", "-p", type=int, default=None, help="Page à récupérer. Toutes si non indiqué.")
            if issubclass(o_entity, TagInterface):
                l_epilog.append(
                    f"""    * lister les {o_entity.entity_titles()} avec d'optionnels filtres sur les infos et les tags : {o_entity.entity_name()} [--infos INFO=VALEUR] [--tags TAG=VALEUR]"""
                )
                o_sub_parser.add_argument("--tags", "-t", type=str, default=None, help=f"Filtrer les {o_entity.entity_titles()} selon les tags")
            else:
                l_epilog.append(f"""    * lister les {o_entity.entity_titles()} avec d'optionnels filtres sur les infos : {o_entity.entity_name()} [--infos INFOS]""")
            l_epilog.append(f"""    * afficher le détail d'une entité : {o_entity.entity_name()} ID""")
            l_epilog.append("""    * effectuer une ACTION sur une entité :""")
            l_epilog.append(f"""        - affiche son emprise : {o_entity.entity_name()} ID --extent [geojson|wkt]""")
            o_sub_parser.add_argument("--extent", type=str, const="geojson", nargs="?", help="Affichage de l'emprise selon le format demandé", choices=["wkt", "geojson"])
            l_epilog.append(f"""        - affiche les entités liées : {o_entity.entity_name()} ID --relative-entities""")
            o_sub_parser.add_argument("--relative-entities", action="store_true", help="Affiche les entités liées.")
            l_epilog.append(f"""        - suppression : {o_entity.entity_name()} ID --delete""")
            o_sub_parser.add_argument("--delete", action="store_true", help="Suppression de l'entité")
            l_epilog.append(f"""        - suppression en cascade : {o_entity.entity_name()} ID --delete --cascade""")
            o_sub_parser.add_argument("--cascade", action="store_true", help="Suppression en cascade")
            l_epilog.append(f"""        - suppression sans confirmation : {o_entity.entity_name()} ID --delete --force""")
            o_sub_parser.add_argument("--force", action="store_true", help="Suppression(s) sans confirmation")

            if o_entity == Annexe:
                l_epilog.append(f"""    * publication / dépublication : `{o_entity.entity_name()} ID [--publish|--unpublish]`""")
                o_sub_parser.add_argument("--publish", action="store_true", help="Publication de l'annexe")
                o_sub_parser.add_argument("--unpublish", action="store_true", help="Dépublication de l'annexe")
                l_epilog.append(f"""    * publication par label : `{o_entity.entity_name()} --publish-by-label label1,label2`""")
                o_sub_parser.add_argument("--publish-by-label", type=str, default=None, help="Publication des annexes portant les labels donnés (ex: label1,label2)")
                l_epilog.append(f"""    * dépublication par label : `{o_entity.entity_name()} --unpublish-by-label label1,label2`""")
                o_sub_parser.add_argument("--unpublish-by-label", type=str, default=None, help="Dépublication des annexes portant les labels donnés (ex: label1,label2)")

            if o_entity == Endpoint:
                l_epilog.append(f"""    * publication de métadonnée : `{o_entity.entity_name()} --publish-metadatas NOM_FICHIER`""")
                o_sub_parser.add_argument("--publish-metadatas", type=str, default=None, help="Publication des métadonnées indiquées (ex: fichier_1,fichier_2)")
                l_epilog.append(f"""    * dépublication de métadonnée : `{o_entity.entity_name()} --unpublish-metadatas NOM_FICHIER`""")
                o_sub_parser.add_argument("--unpublish-metadatas", type=str, default=None, help="Dépublication des métadonnées indiquées (ex: fichier_1,fichier_2)")

            if o_entity == Key:
                l_epilog.append("""    * création de clef : `--f FICHIER`\nExemple du contenu du fichier : `{"key": [{"name": "nom","type": "HASH","type_infos": {"hash": "mon_hash"}}]}`""")
                o_sub_parser.add_argument("--file", "-f", type=str, default=None, help="Chemin vers le fichier décrivant les clefs à créer")

            if o_entity == Upload:
                l_epilog.append(f"""        - ouverture : {o_entity.entity_name()} ID --open""")
                o_sub_parser.add_argument("--open", action="store_true", default=False, help="Rouvrir une livraison fermée")
                l_epilog.append(f"""        - fermeture : {o_entity.entity_name()} ID --close""")
                o_sub_parser.add_argument("--close", action="store_true", default=False, help="Fermer une livraison ouverte")
                l_epilog.append(f"""        - synthèse des vérifications : {o_entity.entity_name()} ID --checks""")
                o_sub_parser.add_argument("--checks", action="store_true", default=False, help="Affiche le bilan des vérifications d'une livraison")
                l_epilog.append(f"""        - suppression de fichiers téléversés : {o_entity.entity_name()} ID --delete-files FILE [FILE]""")
                o_sub_parser.add_argument("--delete-files", type=str, nargs="+", default=None, help="Supprime les fichiers distants indiqués d'une livraison.")
                l_epilog.append(f"""        - suppression auto des fichiers mal téléversés : {o_entity.entity_name()} ID --delete-failed-files""")
                o_sub_parser.add_argument("--delete-failed-files", action="store_true", default=False, help="Supprime les fichiers mal téléversés d'une livraison vérifiées et en erreur.")
                l_epilog.append(f"""    * créer / mettre à jour une livraison (déprécié) : {o_entity.entity_name()} --file FILE [--behavior BEHAVIOR] [--check-before-close]""")
                # TODO déprécié
                o_sub_parser.add_argument("--file", "-f", type=str, default=None, help="(déprécié) Chemin vers le fichier descriptor dont on veut effectuer la livraison)")
                # TODO déprécié
                o_sub_parser.add_argument(
                    "--check-before-close", action="store_true", default=False, help="(déprécié) Si on vérifie l'ensemble de la livraison avant de fermer la livraison (uniquement avec --file|-f)"
                )
                # TODO déprécié
                o_sub_parser.add_argument("--behavior", "-b", choices=UploadAction.BEHAVIORS, default=None, help="(déprécié) Action à effectuer si la livraison existe déjà (uniquement avec -f)")

            if o_entity == ProcessingExecution:
                l_epilog.append(f"""        - annulation de l'exécution de traitement : {o_entity.entity_name()} ID --abort""")
                o_sub_parser.add_argument("--abort", action="store_true", default=False, help="Annule l'exécution de traitement.")

            if issubclass(o_entity, LogsInterface):
                l_epilog.append(f"""        - affichage des logs (uniquement les 1000 première lignes) : {o_entity.entity_name()} ID --logs='1:2/1000'""")
                l_epilog.append(f"""        - affichage des logs (tout en les récupérant 2000 par 2000) : {o_entity.entity_name()} ID --logs='1:0/2000'""")
                l_epilog.append(f"""        - affichage des logs (tout en les filtrant) : {o_entity.entity_name()} ID --logs='1:0/1000|ERROR'""")
                l_epilog.append(f"""        - affichage des logs (la dernière page, maximum 25 lignes) : {o_entity.entity_name()} ID --logs='-1:0/25'""")
                o_sub_parser.add_argument("--logs", type=str, const="-1:0/25", nargs="?", help="Affiche les logs demandés d'une execution")

            l_epilog.append("""""")
            l_epilog.append("""Exemples :""")
            l_epilog.append(f"""    * Listing des {o_entity.entity_title()}s dont le nom contient 'D038' : {o_entity.entity_name()} --infos name=%D038%""")
            l_epilog.append(f"""    * Affichage d'une {o_entity.entity_title()} : {o_entity.entity_name()} 576c85eb-6a2e-4d0c-a0c9-ddb83536e1dc""")
            l_epilog.append(f"""    * Suppression d'une {o_entity.entity_title()} en cascade : {o_entity.entity_name()} 576c85eb-6a2e-4d0c-a0c9-ddb83536e1dc --delete --cascade""")
            if o_entity == Upload:
                l_epilog.append(f"""    * Réouverture d'une livraison : {o_entity.entity_name()} 576c85eb-6a2e-4d0c-a0c9-ddb83536e1dc --open""")
                l_epilog.append(f"""    * Suppression d'un fichier : {o_entity.entity_name()} 576c85eb-6a2e-4d0c-a0c9-ddb83536e1dc --delete-file dossier/fichier.txt""")

            # TODO déprécié
            if o_entity == Static:
                o_sub_parser.add_argument("--file", "-f", type=str, default=None, help="Chemin vers le fichier descriptor dont on veut effectuer la livraison)")
            # TODO déprécié
            if o_entity == Metadata:
                o_sub_parser.add_argument("--file", "-f", type=str, default=None, help="Chemin vers le fichier de métadonnées que l'on veut téléverser)")

            # On met à jour l'épilogue suite à la génération de la doc
            o_sub_parser.epilog = "\n".join(l_epilog)
