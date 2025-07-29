import re
from typing import Optional
from urllib.parse import urlparse

from database_mysql_local.generic_mapping import GenericMapping
from logger_local.LoggerLocal import Logger
from storage_local.aws_s3_storage_local.Storage import Storage

from .internet_domain_local_constants import INTERNET_DOMAIN_PYTHON_PACKAGE_CODE_LOGGER_OBJECT

logger = Logger.create_logger(object=INTERNET_DOMAIN_PYTHON_PACKAGE_CODE_LOGGER_OBJECT)

# TODO Please use url_type_table to identify the type of the URL based on the prefix

# TODO Please mark all private methods as private using __


INTERNET_DOMAIN_SCHEMA_NAME = "internet_domain"
INTERNET_DOMAIN_TABLE_NAME = "internet_domain_table"
INTERNET_DOMAIN_VIEW_NAME = "internet_domain_view"
INTERNET_DOMAIN_ID_COLUMN_NAME = "internet_domain_id"
CONTACT_ENTITY_NAME = "contact"
INTERNET_DOMAIN_ENTITY_NAME = "internet_domain"

# TODO Please remove this const as there are also other webmails (i.e. mail.yahoo.com)
COMMERCIAL_WEBMAIL_DOMAIN = "gmail.com"


class DomainLocal(GenericMapping):
    """
    DomainLocal is a class that uses regular expressions to parse URLs and extract components.
    """

    def __init__(self, default_schema_name: str = INTERNET_DOMAIN_SCHEMA_NAME,
                 default_table_name: str = INTERNET_DOMAIN_TABLE_NAME,
                 default_view_table_name: str = INTERNET_DOMAIN_VIEW_NAME,
                 default_column_name: str = INTERNET_DOMAIN_ID_COLUMN_NAME,
                 default_entity_name1: str = CONTACT_ENTITY_NAME,
                 default_entity_name2: str = INTERNET_DOMAIN_ENTITY_NAME,
                 is_test_data: bool = False):
        self.domain_regex = re.compile(r'^(?:https?://)?(?:www\.)?([^:/\s]+)')
        self.organization_regex = re.compile(r'^(?:https?://)?(?:www\.)?([^.]+)\.')
        self.username_regex = re.compile(r'^https?://(?:([^:/\s]+)@)?')
        self.tld_regex = re.compile(r'^(?:https?://)?(?:www\.)?[^.]+\.(.*?)(?:/|$)')

        GenericMapping.__init__(self, default_schema_name=default_schema_name,
                                default_table_name=default_table_name, default_view_table_name=default_view_table_name,
                                default_column_name=default_column_name,
                                default_entity_name1=default_entity_name1,
                                default_entity_name2=default_entity_name2, is_test_data=is_test_data)

    def get_domain_name(self, url: str) -> Optional[str]:
        """
        Extracts the domain name from a URL.
        """
        if self.valid_url(url):
            match = self.domain_regex.search(url)
            if match:
                return match.group(1)

    def get_organization_name(self, url: str) -> Optional[str]:
        """
        Extracts the organization name from a URL.
        """
        if self.valid_url(url):
            match = self.organization_regex.search(url)
            if match:
                return match.group(1)

    def get_username(self, url: str) -> Optional[str]:
        """
        Extracts the username from a URL.
        """
        if not self.valid_url(url):
            return None
        match = self.username_regex.search(url)
        if match:
            return match.group(1)

    def get_tld(self, url: str) -> Optional[str]:
        """
        Extracts the top-level domain (TLD) from a URL.
        """
        if self.valid_url(url):
            match = self.tld_regex.search(url)
            if match:
                return match.group(1)

    @staticmethod
    def valid_url(url: str) -> bool:
        """
        Validates the URL format.
        """
        if not url:
            return False
        return re.match(r'^(https?://|www\.)', url) is not None

    @staticmethod
    def is_domain(url: str) -> bool:
        """
        Checks if the URL is a domain.
        """
        domain_pattern = re.compile(r"^(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$")
        return re.match(domain_pattern, url) is not None

    @staticmethod
    def is_url(url: str):
        """
        Checks if the URL is a valid URL.
        """
        url_pattern = re.compile(r"^(https?|ftp)://[^\s/$.?#].[^\s]*$")
        return re.match(url_pattern, url) is not None

    # TODO Please either create Sql2Code data structure from `internet_domain`.`internet_domain_table` (preferred)
    # or query for `internet_domain_table`.`is_commercial_webmail` directly
    def is_commercial_webmail(self, url: str) -> bool:
        """Checks if the domain of a URL is a commercial domain (.com)."""
        # The whole concept is to mark which domains are commercial webmail,
        #   i.e. tal@gmail.com doesn't mean I'm working in Gmail, but tal@ibm.com means I'm working in IBM. (edited)
        tld = self.get_tld(url)
        return tld == COMMERCIAL_WEBMAIL_DOMAIN

    # TODO: Split the link_contact_to_domain into 2 functions:
    # 1: link contact to domain
    # 2: link contact to url
    # When we connect the contact to url it calls link contact domain and also to storage's method for url
    # and connect the returned storage_id to profile_id in profile_storage_table
    def link_contact_to_domain(self, contact_id: int, url: str, profile_id: int = None, organization_id: int = None) -> dict:
        """
        Links a contact to a domain.
        Returns a dictionary containing the following information:
        - contact_id
        - url
        - profile_id
        - internet_domain_id
        - contact_internet_domain_id
        - organization_id
        """
        logger.start("link_contact_to_domain", object={
            'contact_id': contact_id, 'url': url})
        if profile_id is None:
            # Try to get it from the database
            profile_id = self.select_one_value_by_column_and_value(
                schema_name='contact', view_table_name='contact_view', select_clause_value='main_profile_id',
                column_name='contact_id', column_value=contact_id)
        try:
            full_domain_name = self.get_domain_name(url)
            tld = self.get_tld(url)
            # TODO Why is the bellow commented? - Next time, please add a comment when commenting.
            # is_commercial_webmail = self.is_commercial_domain(url)
            # At this point lets link the contact to the domain also if it is a commercial webmail
            if not full_domain_name or not tld:
                logger.error(log_message="domain was not extracted successfully from url")
                logger.end(object={"insert_information": {}})
                return {}
            self.set_schema(schema_name='internet_domain')
            # TODO internet_domain_dict = {
            data_to_insert = {
                'domain': full_domain_name,
                'top_level_domain': tld,
                # 'is_commercial_webmail': is_commercial_webmail
                # TODO We should place the main_profile_id of the contact
                'profile_id': profile_id,
                'organization_id': organization_id,
            }
            # check if the domain already exists in the database
            internet_domain_id = self.select_one_value_by_column_and_value(
                select_clause_value='internet_domain_id',
                column_name='domain',
                column_value=full_domain_name,
            )
            if not internet_domain_id:
                # Insert new domain
                internet_domain_id = self.insert(
                    table_name='internet_domain_table',
                    data_dict=data_to_insert, ignore_duplicate=True)
            else:
            # Update existing domain with organization_id
                if organization_id is not None:
                    self.update_by_column_and_value(
                    table_name='internet_domain_table',
                    column_name='internet_domain_id',
                    column_value=internet_domain_id,
                    data_dict={'organization_id': organization_id}
            )

            # link the contact to the domain
            # check if the mapping already exists
            self.set_schema(schema_name='contact_internet_domain')
            contact_internet_domain_id = self.select_one_value_by_where(
                select_clause_value='contact_internet_domain_id',
                view_table_name='contact_internet_domain_view',
                where="contact_id = %s AND internet_domain_id = %s",
                params=(contact_id, internet_domain_id)
            )
            if contact_internet_domain_id is None:
                contact_internet_domain_id = self.insert_mapping(
                    entity_id1=contact_id, entity_id2=internet_domain_id,
                    ignore_duplicate=True
                )
        except Exception as e:
            logger.error("link_contact_to_domain", object={
                'contact_id': contact_id, 'url': url}, data=e)
            raise e
        insert_information = {
            'contact_id': contact_id,
            'url': url,
            'profile_id': profile_id,
            'internet_domain_id': internet_domain_id,
            'contact_internet_domain_id': contact_internet_domain_id,
            'organization_id': organization_id,
        }
        logger.end("link_contact_to_domain", object={
            'contact_internet_domain_id': contact_internet_domain_id})
        return insert_information

    # TODO Let's add url_type and store it in `url_table`.`url_type`
    # TODO Why this methhod is internet_domain is should be either in url-package contact-package or better in contact-url-package (I think it shouldn't be in internet domain package).
    def link_contact_to_url(self, contact_id: int, url: str, profiles_ids: list[int]) -> Optional[dict]:
        if not self.valid_url(url) or not contact_id or not profiles_ids:
            logger.warning("link_contact_to_url: invalid input", object={
                'contact_id': contact_id, 'url': url, 'profiles_ids': profiles_ids})
            return None
        # Add url to url_table
        parsed_url = urlparse(url)
        normalized_url = parsed_url.netloc + parsed_url.path.rstrip('/')

        # Remove 'www.' prefix if it exists
        if normalized_url.startswith('www.'):
            normalized_url = normalized_url[4:]

        # TODO Shal we user url_generic_crud and not self? as url is not internet_domain? Is it mapping?
        url_id = self.select_one_value_by_column_and_value(
            schema_name='url',
            view_table_name='url_view',
            select_clause_value='url_id',
            column_name='url',
            column_value=normalized_url
        )
        if url_id is None:
            url_id = self.insert(
                schema_name='url',
                table_name='url_table',
                # TODO Shall we define two fields original_url and nornalized_url? - As we do in other places.
                data_dict={'url': normalized_url},
                ignore_duplicate=True
            )

        # Get contact's main_profile_id
        # TODO Shall we use contact_generic_crud instead of self?
        main_profile_id = self.select_one_value_by_column_and_value(
            schema_name='contact', view_table_name='contact_view',
            select_clause_value='main_profile_id',
            column_name='contact_id', column_value=contact_id)
        if not main_profile_id:
            profile_id = profiles_ids[0] if len(profiles_ids) > 0 else None
        else:
            profile_id = main_profile_id
        profile_id_str = str(profile_id) if profile_id else 'none'

        # add contact to internet_domain mapping
        # TODO I think it is not clear which schema, I think we should use contact_generic_crud or contact_profile_generic_crud
        # TODO url and domain are two diffrent things, shall we call it contact_url_generic_crud.link_contact_to_url()?
        domain_link_info = self.link_contact_to_domain(contact_id=contact_id, profile_id=profile_id, url=url)

        storage_instance = Storage(is_test_data=self.is_test_data)
        # TODO: How shall we name the file?
        # TODO: When we have asynchronous upload, delete to_upload=False
        # TODO: Shall we let save_url_content_in_storage define the file name? We can change it to get the url id
        file_name = "profile_" + profile_id_str + "_url_" + str(url_id)
        storage_id = storage_instance.save_url_content_in_storage(
            url=url, file_name=file_name, to_upload=False
        )

        # link profile to storage
        # Shall we improve performace if we use profile_storage_mapping
        self.set_schema(schema_name='profile_storage')
        # TODO profile_storage_ids_list
        profiles_storage_ids: list[int] = []
        for profile_id in profiles_ids:
            # TODO profile_storage_mapping.insert_mapping
            profile_storage_id = self.insert_mapping(
                entity_id1=profile_id, entity_id2=storage_id,
                entity_name1='profile', entity_name2='storage',
                ignore_duplicate=True
            )
            profiles_storage_ids.append(profile_storage_id)
        self.set_schema(schema_name=INTERNET_DOMAIN_SCHEMA_NAME)
        insert_results = {
            'contact_id': contact_id,
            'url': url,
            'profile_id': profile_id,
            'url_id': url_id,
            'storage_id': storage_id,
            'profiles_storage_ids': profiles_storage_ids,
            'internet_domain_id': domain_link_info.get('internet_domain_id'),
            'contact_internet_domain_id': domain_link_info.get('contact_internet_domain_id')
        }
        return insert_results

    def is_email_assign_profile_organization_to_people(self, domain: str) -> bool:
        logger.start()
        tup = self.select_one_value_by_column_and_value(
            select_clause_value="is_email_assign_profile_organization_to_people",
            column_name="domain",
            column_value=domain,
            order_by="internet_domain_id DESC"
        ) or False
        logger.end(object={"tup": tup})
        return bool(tup)

    def is_url_assign_profile_organization_to_people(self, domain: str) -> bool:
        logger.start()
        tup = self.select_one_value_by_column_and_value(
            select_clause_value="is_url_assign_profile_organization_to_people",
            column_name="domain",
            column_value=domain,
            order_by="internet_domain_id DESC"
        ) or False
        logger.end(object={"tup": tup})
        return bool(tup)
