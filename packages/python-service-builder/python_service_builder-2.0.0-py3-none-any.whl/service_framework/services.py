# Copyright 2022 David Harcombe
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import annotations

import aenum as enum

from . import ServiceDefinition, lazy_property
from .list_services import ServiceFinder


class Service(enum.Enum):
  """Defines the generic Enum for any service.

  Raises:
      ValueError: if no enum is defined.
  """
  @lazy_property
  def definition(self) -> ServiceDefinition:
    """Fetch the ServiceDefinition.

    Lazily returns the dataclass containing the service definition
    details. It has to be lazy, as it can't be defined at
    initialization time.

    Returns:
        ServiceDefinition: the service definition
    """
    return self._value_

  @classmethod
  def create_service(cls, name: str) -> Service:
    finder = ServiceFinder()
    if service := finder(name.lower()):
      new_service = object.__new__(cls)
      new_service._name_ = name.upper()
      new_service._value_ = service
      cls._value2member_map_[name.upper()] = new_service
      return new_service

  @classmethod
  def _missing_(cls, value) -> Service:
    if service := cls.__members__.get(value.upper(), None):
      return service
    else:
      return cls.create_service(value)

  @classmethod
  def from_value(cls, value: str) -> Service:
    """Creates a service enum from the name of the service.

    Args:
        value (str): the service name

    Raises:
        ValueError: no service found

    Returns:
        S: the service definition
    """
    if service := cls.__members__.get(value.upper(), None):
      return service

    else:
      return cls.create_service(value)

  ABUSIVEEXPERIENCEREPORT = ServiceDefinition(
      'abusiveexperiencereport', 'v1', 'https://abusiveexperiencereport.googleapis.com/$discovery/rest?version=v1')
  ACCELERATEDMOBILEPAGEURL = ServiceDefinition(
      'acceleratedmobilepageurl', 'v1', 'https://acceleratedmobilepageurl.googleapis.com/$discovery/rest?version=v1')
  ACCESSAPPROVAL = ServiceDefinition(
      'accessapproval', 'v1', 'https://accessapproval.googleapis.com/$discovery/rest?version=v1')
  ACCESSCONTEXTMANAGER = ServiceDefinition(
      'accesscontextmanager', 'v1', 'https://accesscontextmanager.googleapis.com/$discovery/rest?version=v1')
  ADDRESSVALIDATION = ServiceDefinition(
      'addressvalidation', 'v1', 'https://addressvalidation.googleapis.com/$discovery/rest?version=v1')
  ADEXCHANGEBUYER2 = ServiceDefinition(
      'adexchangebuyer2', 'v2beta1', 'https://adexchangebuyer.googleapis.com/$discovery/rest?version=v2beta1')
  ADEXPERIENCEREPORT = ServiceDefinition(
      'adexperiencereport', 'v1', 'https://adexperiencereport.googleapis.com/$discovery/rest?version=v1')
  ADMIN = ServiceDefinition(
      'admin', 'reports_v1', 'https://admin.googleapis.com/$discovery/rest?version=reports_v1')
  ADMOB = ServiceDefinition(
      'admob', 'v1', 'https://admob.googleapis.com/$discovery/rest?version=v1')
  ADSENSE = ServiceDefinition(
      'adsense', 'v2', 'https://adsense.googleapis.com/$discovery/rest?version=v2')
  ADSENSEPLATFORM = ServiceDefinition(
      'adsenseplatform', 'v1', 'https://adsenseplatform.googleapis.com/$discovery/rest?version=v1')
  ADVISORYNOTIFICATIONS = ServiceDefinition(
      'advisorynotifications', 'v1', 'https://advisorynotifications.googleapis.com/$discovery/rest?version=v1')
  AIPLATFORM = ServiceDefinition(
      'aiplatform', 'v1', 'https://aiplatform.googleapis.com/$discovery/rest?version=v1')
  AIRQUALITY = ServiceDefinition(
      'airquality', 'v1', 'https://airquality.googleapis.com/$discovery/rest?version=v1')
  ALERTCENTER = ServiceDefinition(
      'alertcenter', 'v1beta1', 'https://alertcenter.googleapis.com/$discovery/rest?version=v1beta1')
  ALLOYDB = ServiceDefinition(
      'alloydb', 'v1', 'https://alloydb.googleapis.com/$discovery/rest?version=v1')
  ANALYTICS = ServiceDefinition(
      'analytics', 'v3', 'https://analytics.googleapis.com/$discovery/rest?version=v3')
  ANALYTICSADMIN = ServiceDefinition(
      'analyticsadmin', 'v1beta', 'https://analyticsadmin.googleapis.com/$discovery/rest?version=v1beta')
  ANALYTICSDATA = ServiceDefinition(
      'analyticsdata', 'v1beta', 'https://analyticsdata.googleapis.com/$discovery/rest?version=v1beta')
  ANALYTICSHUB = ServiceDefinition(
      'analyticshub', 'v1', 'https://analyticshub.googleapis.com/$discovery/rest?version=v1')
  ANDROIDDEVICEPROVISIONING = ServiceDefinition(
      'androiddeviceprovisioning', 'v1', 'https://androiddeviceprovisioning.googleapis.com/$discovery/rest?version=v1')
  ANDROIDENTERPRISE = ServiceDefinition(
      'androidenterprise', 'v1', 'https://androidenterprise.googleapis.com/$discovery/rest?version=v1')
  ANDROIDMANAGEMENT = ServiceDefinition(
      'androidmanagement', 'v1', 'https://androidmanagement.googleapis.com/$discovery/rest?version=v1')
  ANDROIDPUBLISHER = ServiceDefinition(
      'androidpublisher', 'v3', 'https://androidpublisher.googleapis.com/$discovery/rest?version=v3')
  APIGATEWAY = ServiceDefinition(
      'apigateway', 'v1', 'https://apigateway.googleapis.com/$discovery/rest?version=v1')
  APIGEE = ServiceDefinition(
      'apigee', 'v1', 'https://apigee.googleapis.com/$discovery/rest?version=v1')
  APIGEEREGISTRY = ServiceDefinition(
      'apigeeregistry', 'v1', 'https://apigeeregistry.googleapis.com/$discovery/rest?version=v1')
  APIHUB = ServiceDefinition(
      'apihub', 'v1', 'https://apihub.googleapis.com/$discovery/rest?version=v1')
  APIKEYS = ServiceDefinition(
      'apikeys', 'v2', 'https://apikeys.googleapis.com/$discovery/rest?version=v2')
  APIM = ServiceDefinition(
      'apim', 'v1alpha', 'https://apim.googleapis.com/$discovery/rest?version=v1alpha')
  APPENGINE = ServiceDefinition(
      'appengine', 'v1', 'https://appengine.googleapis.com/$discovery/rest?version=v1')
  APPHUB = ServiceDefinition(
      'apphub', 'v1', 'https://apphub.googleapis.com/$discovery/rest?version=v1')
  AREA120TABLES = ServiceDefinition(
      'area120tables', 'v1alpha1', 'https://area120tables.googleapis.com/$discovery/rest?version=v1alpha1')
  AREAINSIGHTS = ServiceDefinition(
      'areainsights', 'v1', 'https://areainsights.googleapis.com/$discovery/rest?version=v1')
  ARTIFACTREGISTRY = ServiceDefinition(
      'artifactregistry', 'v1', 'https://artifactregistry.googleapis.com/$discovery/rest?version=v1')
  ASSUREDWORKLOADS = ServiceDefinition(
      'assuredworkloads', 'v1', 'https://assuredworkloads.googleapis.com/$discovery/rest?version=v1')
  AUTHORIZEDBUYERSMARKETPLACE = ServiceDefinition(
      'authorizedbuyersmarketplace', 'v1', 'https://authorizedbuyersmarketplace.googleapis.com/$discovery/rest?version=v1')
  BACKUPDR = ServiceDefinition(
      'backupdr', 'v1', 'https://backupdr.googleapis.com/$discovery/rest?version=v1')
  BAREMETALSOLUTION = ServiceDefinition(
      'baremetalsolution', 'v2', 'https://baremetalsolution.googleapis.com/$discovery/rest?version=v2')
  BATCH = ServiceDefinition(
      'batch', 'v1', 'https://batch.googleapis.com/$discovery/rest?version=v1')
  BEYONDCORP = ServiceDefinition(
      'beyondcorp', 'v1', 'https://beyondcorp.googleapis.com/$discovery/rest?version=v1')
  BIGLAKE = ServiceDefinition(
      'biglake', 'v1', 'https://biglake.googleapis.com/$discovery/rest?version=v1')
  BIGQUERY = ServiceDefinition(
      'bigquery', 'v2', 'https://bigquery.googleapis.com/$discovery/rest?version=v2')
  BIGQUERYCONNECTION = ServiceDefinition(
      'bigqueryconnection', 'v1', 'https://bigqueryconnection.googleapis.com/$discovery/rest?version=v1')
  BIGQUERYDATAPOLICY = ServiceDefinition(
      'bigquerydatapolicy', 'v1', 'https://bigquerydatapolicy.googleapis.com/$discovery/rest?version=v1')
  BIGQUERYDATATRANSFER = ServiceDefinition(
      'bigquerydatatransfer', 'v1', 'https://bigquerydatatransfer.googleapis.com/$discovery/rest?version=v1')
  BIGQUERYRESERVATION = ServiceDefinition(
      'bigqueryreservation', 'v1', 'https://bigqueryreservation.googleapis.com/$discovery/rest?version=v1')
  BIGTABLEADMIN = ServiceDefinition(
      'bigtableadmin', 'v2', 'https://bigtableadmin.googleapis.com/$discovery/rest?version=v2')
  BILLINGBUDGETS = ServiceDefinition(
      'billingbudgets', 'v1', 'https://billingbudgets.googleapis.com/$discovery/rest?version=v1')
  BINARYAUTHORIZATION = ServiceDefinition(
      'binaryauthorization', 'v1', 'https://binaryauthorization.googleapis.com/$discovery/rest?version=v1')
  BLOCKCHAINNODEENGINE = ServiceDefinition(
      'blockchainnodeengine', 'v1', 'https://blockchainnodeengine.googleapis.com/$discovery/rest?version=v1')
  BLOGGER = ServiceDefinition(
      'blogger', 'v3', 'https://blogger.googleapis.com/$discovery/rest?version=v3')
  BOOKS = ServiceDefinition(
      'books', 'v1', 'https://books.googleapis.com/$discovery/rest?version=v1')
  BUSINESSPROFILEPERFORMANCE = ServiceDefinition(
      'businessprofileperformance', 'v1', 'https://businessprofileperformance.googleapis.com/$discovery/rest?version=v1')
  CALENDAR = ServiceDefinition(
      'calendar', 'v3', 'https://calendar-json.googleapis.com/$discovery/rest?version=v3')
  CERTIFICATEMANAGER = ServiceDefinition(
      'certificatemanager', 'v1', 'https://certificatemanager.googleapis.com/$discovery/rest?version=v1')
  CHAT = ServiceDefinition(
      'chat', 'v1', 'https://chat.googleapis.com/$discovery/rest?version=v1')
  CHECKS = ServiceDefinition(
      'checks', 'v1alpha', 'https://checks.googleapis.com/$discovery/rest?version=v1alpha')
  CHROMEMANAGEMENT = ServiceDefinition(
      'chromemanagement', 'v1', 'https://chromemanagement.googleapis.com/$discovery/rest?version=v1')
  CHROMEPOLICY = ServiceDefinition(
      'chromepolicy', 'v1', 'https://chromepolicy.googleapis.com/$discovery/rest?version=v1')
  CHROMEUXREPORT = ServiceDefinition(
      'chromeuxreport', 'v1', 'https://chromeuxreport.googleapis.com/$discovery/rest?version=v1')
  CIVICINFO = ServiceDefinition(
      'civicinfo', 'v2', 'https://civicinfo.googleapis.com/$discovery/rest?version=v2')
  CLASSROOM = ServiceDefinition(
      'classroom', 'v1', 'https://classroom.googleapis.com/$discovery/rest?version=v1')
  CLOUDASSET = ServiceDefinition(
      'cloudasset', 'v1', 'https://cloudasset.googleapis.com/$discovery/rest?version=v1')
  CLOUDBILLING = ServiceDefinition(
      'cloudbilling', 'v1', 'https://cloudbilling.googleapis.com/$discovery/rest?version=v1')
  CLOUDBUILD = ServiceDefinition(
      'cloudbuild', 'v2', 'https://cloudbuild.googleapis.com/$discovery/rest?version=v2')
  CLOUDCHANNEL = ServiceDefinition(
      'cloudchannel', 'v1', 'https://cloudchannel.googleapis.com/$discovery/rest?version=v1')
  CLOUDCONTROLSPARTNER = ServiceDefinition(
      'cloudcontrolspartner', 'v1', 'https://cloudcontrolspartner.googleapis.com/$discovery/rest?version=v1')
  CLOUDDEPLOY = ServiceDefinition(
      'clouddeploy', 'v1', 'https://clouddeploy.googleapis.com/$discovery/rest?version=v1')
  CLOUDERRORREPORTING = ServiceDefinition(
      'clouderrorreporting', 'v1beta1', 'https://clouderrorreporting.googleapis.com/$discovery/rest?version=v1beta1')
  CLOUDFUNCTIONS = ServiceDefinition(
      'cloudfunctions', 'v2', 'https://cloudfunctions.googleapis.com/$discovery/rest?version=v2')
  CLOUDIDENTITY = ServiceDefinition(
      'cloudidentity', 'v1', 'https://cloudidentity.googleapis.com/$discovery/rest?version=v1')
  CLOUDKMS = ServiceDefinition(
      'cloudkms', 'v1', 'https://cloudkms.googleapis.com/$discovery/rest?version=v1')
  CLOUDLOCATIONFINDER = ServiceDefinition(
      'cloudlocationfinder', 'v1alpha', 'https://cloudlocationfinder.googleapis.com/$discovery/rest?version=v1alpha')
  CLOUDPROFILER = ServiceDefinition(
      'cloudprofiler', 'v2', 'https://cloudprofiler.googleapis.com/$discovery/rest?version=v2')
  CLOUDRESOURCEMANAGER = ServiceDefinition(
      'cloudresourcemanager', 'v3', 'https://cloudresourcemanager.googleapis.com/$discovery/rest?version=v3')
  CLOUDSCHEDULER = ServiceDefinition(
      'cloudscheduler', 'v1', 'https://cloudscheduler.googleapis.com/$discovery/rest?version=v1')
  CLOUDSEARCH = ServiceDefinition(
      'cloudsearch', 'v1', 'https://cloudsearch.googleapis.com/$discovery/rest?version=v1')
  CLOUDSHELL = ServiceDefinition(
      'cloudshell', 'v1', 'https://cloudshell.googleapis.com/$discovery/rest?version=v1')
  CLOUDSUPPORT = ServiceDefinition(
      'cloudsupport', 'v2', 'https://cloudsupport.googleapis.com/$discovery/rest?version=v2')
  CLOUDTASKS = ServiceDefinition(
      'cloudtasks', 'v2', 'https://cloudtasks.googleapis.com/$discovery/rest?version=v2')
  CLOUDTRACE = ServiceDefinition(
      'cloudtrace', 'v2', 'https://cloudtrace.googleapis.com/$discovery/rest?version=v2')
  COMPOSER = ServiceDefinition(
      'composer', 'v1', 'https://composer.googleapis.com/$discovery/rest?version=v1')
  COMPUTE = ServiceDefinition(
      'compute', 'v1', 'https://www.googleapis.com/discovery/v1/apis/compute/v1/rest')
  CONFIG = ServiceDefinition(
      'config', 'v1', 'https://config.googleapis.com/$discovery/rest?version=v1')
  CONNECTORS = ServiceDefinition(
      'connectors', 'v2', 'https://connectors.googleapis.com/$discovery/rest?version=v2')
  CONTACTCENTERAIPLATFORM = ServiceDefinition(
      'contactcenteraiplatform', 'v1alpha1', 'https://contactcenteraiplatform.googleapis.com/$discovery/rest?version=v1alpha1')
  CONTACTCENTERINSIGHTS = ServiceDefinition(
      'contactcenterinsights', 'v1', 'https://contactcenterinsights.googleapis.com/$discovery/rest?version=v1')
  CONTAINER = ServiceDefinition(
      'container', 'v1', 'https://container.googleapis.com/$discovery/rest?version=v1')
  CONTAINERANALYSIS = ServiceDefinition(
      'containeranalysis', 'v1', 'https://containeranalysis.googleapis.com/$discovery/rest?version=v1')
  CONTENT = ServiceDefinition(
      'content', 'v2.1', 'https://shoppingcontent.googleapis.com/$discovery/rest?version=v2.1')
  CONTENTWAREHOUSE = ServiceDefinition(
      'contentwarehouse', 'v1', 'https://contentwarehouse.googleapis.com/$discovery/rest?version=v1')
  CSS = ServiceDefinition(
      'css', 'v1', 'https://css.googleapis.com/$discovery/rest?version=v1')
  CUSTOMSEARCH = ServiceDefinition(
      'customsearch', 'v1', 'https://customsearch.googleapis.com/$discovery/rest?version=v1')
  DATACATALOG = ServiceDefinition(
      'datacatalog', 'v1', 'https://datacatalog.googleapis.com/$discovery/rest?version=v1')
  DATAFLOW = ServiceDefinition(
      'dataflow', 'v1b3', 'https://dataflow.googleapis.com/$discovery/rest?version=v1b3')
  DATAFORM = ServiceDefinition(
      'dataform', 'v1beta1', 'https://dataform.googleapis.com/$discovery/rest?version=v1beta1')
  DATAFUSION = ServiceDefinition(
      'datafusion', 'v1', 'https://datafusion.googleapis.com/$discovery/rest?version=v1')
  DATALABELING = ServiceDefinition(
      'datalabeling', 'v1beta1', 'https://datalabeling.googleapis.com/$discovery/rest?version=v1beta1')
  DATALINEAGE = ServiceDefinition(
      'datalineage', 'v1', 'https://datalineage.googleapis.com/$discovery/rest?version=v1')
  DATAMIGRATION = ServiceDefinition(
      'datamigration', 'v1', 'https://datamigration.googleapis.com/$discovery/rest?version=v1')
  DATAPIPELINES = ServiceDefinition(
      'datapipelines', 'v1', 'https://datapipelines.googleapis.com/$discovery/rest?version=v1')
  DATAPLEX = ServiceDefinition(
      'dataplex', 'v1', 'https://dataplex.googleapis.com/$discovery/rest?version=v1')
  DATAPORTABILITY = ServiceDefinition(
      'dataportability', 'v1', 'https://dataportability.googleapis.com/$discovery/rest?version=v1')
  DATAPROC = ServiceDefinition(
      'dataproc', 'v1', 'https://dataproc.googleapis.com/$discovery/rest?version=v1')
  DATASTORE = ServiceDefinition(
      'datastore', 'v1', 'https://datastore.googleapis.com/$discovery/rest?version=v1')
  DATASTREAM = ServiceDefinition(
      'datastream', 'v1', 'https://datastream.googleapis.com/$discovery/rest?version=v1')
  DEPLOYMENTMANAGER = ServiceDefinition(
      'deploymentmanager', 'v2', 'https://deploymentmanager.googleapis.com/$discovery/rest?version=v2')
  DEVELOPERCONNECT = ServiceDefinition(
      'developerconnect', 'v1', 'https://developerconnect.googleapis.com/$discovery/rest?version=v1')
  DFAREPORTING = ServiceDefinition(
      'dfareporting', 'v4', 'https://dfareporting.googleapis.com/$discovery/rest?version=v4')
  DIALOGFLOW = ServiceDefinition(
      'dialogflow', 'v3', 'https://dialogflow.googleapis.com/$discovery/rest?version=v3')
  DIGITALASSETLINKS = ServiceDefinition(
      'digitalassetlinks', 'v1', 'https://digitalassetlinks.googleapis.com/$discovery/rest?version=v1')
  DISCOVERY = ServiceDefinition(
      'discovery', 'v1', 'https://discovery.googleapis.com/$discovery/rest?version=v1')
  DISCOVERYENGINE = ServiceDefinition(
      'discoveryengine', 'v1', 'https://discoveryengine.googleapis.com/$discovery/rest?version=v1')
  DISPLAYVIDEO = ServiceDefinition(
      'displayvideo', 'v4', 'https://displayvideo.googleapis.com/$discovery/rest?version=v4')
  DLP = ServiceDefinition(
      'dlp', 'v2', 'https://dlp.googleapis.com/$discovery/rest?version=v2')
  DNS = ServiceDefinition(
      'dns', 'v1', 'https://dns.googleapis.com/$discovery/rest?version=v1')
  DOCS = ServiceDefinition(
      'docs', 'v1', 'https://docs.googleapis.com/$discovery/rest?version=v1')
  DOCUMENTAI = ServiceDefinition(
      'documentai', 'v1', 'https://documentai.googleapis.com/$discovery/rest?version=v1')
  DOMAINS = ServiceDefinition(
      'domains', 'v1', 'https://domains.googleapis.com/$discovery/rest?version=v1')
  DOUBLECLICKBIDMANAGER = ServiceDefinition(
      'doubleclickbidmanager', 'v2', 'https://doubleclickbidmanager.googleapis.com/$discovery/rest?version=v2')
  DOUBLECLICKSEARCH = ServiceDefinition(
      'doubleclicksearch', 'v2', 'https://doubleclicksearch.googleapis.com/$discovery/rest?version=v2')
  DRIVE = ServiceDefinition(
      'drive', 'v3', 'https://www.googleapis.com/discovery/v1/apis/drive/v3/rest')
  DRIVEACTIVITY = ServiceDefinition(
      'driveactivity', 'v2', 'https://driveactivity.googleapis.com/$discovery/rest?version=v2')
  DRIVELABELS = ServiceDefinition(
      'drivelabels', 'v2', 'https://drivelabels.googleapis.com/$discovery/rest?version=v2')
  ESSENTIALCONTACTS = ServiceDefinition(
      'essentialcontacts', 'v1', 'https://essentialcontacts.googleapis.com/$discovery/rest?version=v1')
  EVENTARC = ServiceDefinition(
      'eventarc', 'v1', 'https://eventarc.googleapis.com/$discovery/rest?version=v1')
  FACTCHECKTOOLS = ServiceDefinition(
      'factchecktools', 'v1alpha1', 'https://factchecktools.googleapis.com/$discovery/rest?version=v1alpha1')
  FCM = ServiceDefinition(
      'fcm', 'v1', 'https://fcm.googleapis.com/$discovery/rest?version=v1')
  FCMDATA = ServiceDefinition(
      'fcmdata', 'v1beta1', 'https://fcmdata.googleapis.com/$discovery/rest?version=v1beta1')
  FILE = ServiceDefinition(
      'file', 'v1', 'https://file.googleapis.com/$discovery/rest?version=v1')
  FIREBASE = ServiceDefinition(
      'firebase', 'v1beta1', 'https://firebase.googleapis.com/$discovery/rest?version=v1beta1')
  FIREBASEAPPCHECK = ServiceDefinition(
      'firebaseappcheck', 'v1', 'https://firebaseappcheck.googleapis.com/$discovery/rest?version=v1')
  FIREBASEAPPDISTRIBUTION = ServiceDefinition(
      'firebaseappdistribution', 'v1', 'https://firebaseappdistribution.googleapis.com/$discovery/rest?version=v1')
  FIREBASEAPPHOSTING = ServiceDefinition(
      'firebaseapphosting', 'v1', 'https://firebaseapphosting.googleapis.com/$discovery/rest?version=v1')
  FIREBASEDATABASE = ServiceDefinition(
      'firebasedatabase', 'v1beta', 'https://firebasedatabase.googleapis.com/$discovery/rest?version=v1beta')
  FIREBASEDATACONNECT = ServiceDefinition(
      'firebasedataconnect', 'v1', 'https://firebasedataconnect.googleapis.com/$discovery/rest?version=v1')
  FIREBASEDYNAMICLINKS = ServiceDefinition(
      'firebasedynamiclinks', 'v1', 'https://firebasedynamiclinks.googleapis.com/$discovery/rest?version=v1')
  FIREBASEHOSTING = ServiceDefinition(
      'firebasehosting', 'v1', 'https://firebasehosting.googleapis.com/$discovery/rest?version=v1')
  FIREBASEML = ServiceDefinition(
      'firebaseml', 'v1', 'https://firebaseml.googleapis.com/$discovery/rest?version=v1')
  FIREBASERULES = ServiceDefinition(
      'firebaserules', 'v1', 'https://firebaserules.googleapis.com/$discovery/rest?version=v1')
  FIREBASESTORAGE = ServiceDefinition(
      'firebasestorage', 'v1beta', 'https://firebasestorage.googleapis.com/$discovery/rest?version=v1beta')
  FIRESTORE = ServiceDefinition(
      'firestore', 'v1', 'https://firestore.googleapis.com/$discovery/rest?version=v1')
  FITNESS = ServiceDefinition(
      'fitness', 'v1', 'https://fitness.googleapis.com/$discovery/rest?version=v1')
  FORMS = ServiceDefinition(
      'forms', 'v1', 'https://forms.googleapis.com/$discovery/rest?version=v1')
  GAMES = ServiceDefinition(
      'games', 'v1', 'https://games.googleapis.com/$discovery/rest?version=v1')
  GAMESCONFIGURATION = ServiceDefinition('gamesConfiguration', 'v1configuration',
                                         'https://gamesconfiguration.googleapis.com/$discovery/rest?version=v1configuration')
  GAMESMANAGEMENT = ServiceDefinition('gamesManagement', 'v1management',
                                      'https://gamesmanagement.googleapis.com/$discovery/rest?version=v1management')
  GKEBACKUP = ServiceDefinition(
      'gkebackup', 'v1', 'https://gkebackup.googleapis.com/$discovery/rest?version=v1')
  GKEHUB = ServiceDefinition(
      'gkehub', 'v2', 'https://gkehub.googleapis.com/$discovery/rest?version=v2')
  GKEONPREM = ServiceDefinition(
      'gkeonprem', 'v1', 'https://gkeonprem.googleapis.com/$discovery/rest?version=v1')
  GMAIL = ServiceDefinition(
      'gmail', 'v1', 'https://gmail.googleapis.com/$discovery/rest?version=v1')
  GMAILPOSTMASTERTOOLS = ServiceDefinition(
      'gmailpostmastertools', 'v1', 'https://gmailpostmastertools.googleapis.com/$discovery/rest?version=v1')
  GROUPSMIGRATION = ServiceDefinition(
      'groupsmigration', 'v1', 'https://groupsmigration.googleapis.com/$discovery/rest?version=v1')
  GROUPSSETTINGS = ServiceDefinition(
      'groupssettings', 'v1', 'https://groupssettings.googleapis.com/$discovery/rest?version=v1')
  HEALTHCARE = ServiceDefinition(
      'healthcare', 'v1', 'https://healthcare.googleapis.com/$discovery/rest?version=v1')
  HOMEGRAPH = ServiceDefinition(
      'homegraph', 'v1', 'https://homegraph.googleapis.com/$discovery/rest?version=v1')
  IAM = ServiceDefinition(
      'iam', 'v2', 'https://iam.googleapis.com/$discovery/rest?version=v2')
  IAMCREDENTIALS = ServiceDefinition(
      'iamcredentials', 'v1', 'https://iamcredentials.googleapis.com/$discovery/rest?version=v1')
  IAP = ServiceDefinition(
      'iap', 'v1', 'https://iap.googleapis.com/$discovery/rest?version=v1')
  IDENTITYTOOLKIT = ServiceDefinition(
      'identitytoolkit', 'v3', 'https://identitytoolkit.googleapis.com/$discovery/rest?version=v3')
  IDS = ServiceDefinition(
      'ids', 'v1', 'https://ids.googleapis.com/$discovery/rest?version=v1')
  INDEXING = ServiceDefinition(
      'indexing', 'v3', 'https://indexing.googleapis.com/$discovery/rest?version=v3')
  INTEGRATIONS = ServiceDefinition(
      'integrations', 'v1', 'https://integrations.googleapis.com/$discovery/rest?version=v1')
  JOBS = ServiceDefinition(
      'jobs', 'v4', 'https://jobs.googleapis.com/$discovery/rest?version=v4')
  KEEP = ServiceDefinition(
      'keep', 'v1', 'https://keep.googleapis.com/$discovery/rest?version=v1')
  KGSEARCH = ServiceDefinition(
      'kgsearch', 'v1', 'https://kgsearch.googleapis.com/$discovery/rest?version=v1')
  KMSINVENTORY = ServiceDefinition(
      'kmsinventory', 'v1', 'https://kmsinventory.googleapis.com/$discovery/rest?version=v1')
  LANGUAGE = ServiceDefinition(
      'language', 'v2', 'https://language.googleapis.com/$discovery/rest?version=v2')
  LIBRARYAGENT = ServiceDefinition(
      'libraryagent', 'v1', 'https://libraryagent.googleapis.com/$discovery/rest?version=v1')
  LICENSING = ServiceDefinition(
      'licensing', 'v1', 'https://licensing.googleapis.com/$discovery/rest?version=v1')
  LIFESCIENCES = ServiceDefinition(
      'lifesciences', 'v2beta', 'https://lifesciences.googleapis.com/$discovery/rest?version=v2beta')
  LOCALSERVICES = ServiceDefinition(
      'localservices', 'v1', 'https://localservices.googleapis.com/$discovery/rest?version=v1')
  LOGGING = ServiceDefinition(
      'logging', 'v2', 'https://logging.googleapis.com/$discovery/rest?version=v2')
  LOOKER = ServiceDefinition(
      'looker', 'v1', 'https://looker.googleapis.com/$discovery/rest?version=v1')
  MANAGEDIDENTITIES = ServiceDefinition(
      'managedidentities', 'v1', 'https://managedidentities.googleapis.com/$discovery/rest?version=v1')
  MANAGEDKAFKA = ServiceDefinition(
      'managedkafka', 'v1', 'https://managedkafka.googleapis.com/$discovery/rest?version=v1')
  MANUFACTURERS = ServiceDefinition(
      'manufacturers', 'v1', 'https://manufacturers.googleapis.com/$discovery/rest?version=v1')
  MARKETINGPLATFORMADMIN = ServiceDefinition(
      'marketingplatformadmin', 'v1alpha', 'https://marketingplatformadmin.googleapis.com/$discovery/rest?version=v1alpha')
  MEET = ServiceDefinition(
      'meet', 'v2', 'https://meet.googleapis.com/$discovery/rest?version=v2')
  MEMCACHE = ServiceDefinition(
      'memcache', 'v1', 'https://memcache.googleapis.com/$discovery/rest?version=v1')
  MERCHANTAPI = ServiceDefinition('merchantapi', 'reviews_v1beta',
                                  'https://merchantapi.googleapis.com/$discovery/rest?version=reviews_v1beta')
  METASTORE = ServiceDefinition(
      'metastore', 'v2', 'https://metastore.googleapis.com/$discovery/rest?version=v2')
  MIGRATIONCENTER = ServiceDefinition(
      'migrationcenter', 'v1', 'https://migrationcenter.googleapis.com/$discovery/rest?version=v1')
  ML = ServiceDefinition(
      'ml', 'v1', 'https://ml.googleapis.com/$discovery/rest?version=v1')
  MONITORING = ServiceDefinition(
      'monitoring', 'v3', 'https://monitoring.googleapis.com/$discovery/rest?version=v3')
  MYBUSINESSACCOUNTMANAGEMENT = ServiceDefinition(
      'mybusinessaccountmanagement', 'v1', 'https://mybusinessaccountmanagement.googleapis.com/$discovery/rest?version=v1')
  MYBUSINESSBUSINESSINFORMATION = ServiceDefinition(
      'mybusinessbusinessinformation', 'v1', 'https://mybusinessbusinessinformation.googleapis.com/$discovery/rest?version=v1')
  MYBUSINESSLODGING = ServiceDefinition(
      'mybusinesslodging', 'v1', 'https://mybusinesslodging.googleapis.com/$discovery/rest?version=v1')
  MYBUSINESSNOTIFICATIONS = ServiceDefinition(
      'mybusinessnotifications', 'v1', 'https://mybusinessnotifications.googleapis.com/$discovery/rest?version=v1')
  MYBUSINESSPLACEACTIONS = ServiceDefinition(
      'mybusinessplaceactions', 'v1', 'https://mybusinessplaceactions.googleapis.com/$discovery/rest?version=v1')
  MYBUSINESSQANDA = ServiceDefinition(
      'mybusinessqanda', 'v1', 'https://mybusinessqanda.googleapis.com/$discovery/rest?version=v1')
  MYBUSINESSVERIFICATIONS = ServiceDefinition(
      'mybusinessverifications', 'v1', 'https://mybusinessverifications.googleapis.com/$discovery/rest?version=v1')
  NETAPP = ServiceDefinition(
      'netapp', 'v1', 'https://netapp.googleapis.com/$discovery/rest?version=v1')
  NETWORKCONNECTIVITY = ServiceDefinition(
      'networkconnectivity', 'v1', 'https://networkconnectivity.googleapis.com/$discovery/rest?version=v1')
  NETWORKMANAGEMENT = ServiceDefinition(
      'networkmanagement', 'v1', 'https://networkmanagement.googleapis.com/$discovery/rest?version=v1')
  NETWORKSECURITY = ServiceDefinition(
      'networksecurity', 'v1', 'https://networksecurity.googleapis.com/$discovery/rest?version=v1')
  NETWORKSERVICES = ServiceDefinition(
      'networkservices', 'v1', 'https://networkservices.googleapis.com/$discovery/rest?version=v1')
  NOTEBOOKS = ServiceDefinition(
      'notebooks', 'v2', 'https://notebooks.googleapis.com/$discovery/rest?version=v2')
  OAUTH2 = ServiceDefinition(
      'oauth2', 'v2', 'https://www.googleapis.com/discovery/v1/apis/oauth2/v2/rest')
  OBSERVABILITY = ServiceDefinition(
      'observability', 'v1', 'https://observability.googleapis.com/$discovery/rest?version=v1')
  ONDEMANDSCANNING = ServiceDefinition(
      'ondemandscanning', 'v1', 'https://ondemandscanning.googleapis.com/$discovery/rest?version=v1')
  ORACLEDATABASE = ServiceDefinition(
      'oracledatabase', 'v1', 'https://oracledatabase.googleapis.com/$discovery/rest?version=v1')
  ORGPOLICY = ServiceDefinition(
      'orgpolicy', 'v2', 'https://orgpolicy.googleapis.com/$discovery/rest?version=v2')
  OSCONFIG = ServiceDefinition(
      'osconfig', 'v2', 'https://osconfig.googleapis.com/$discovery/rest?version=v2')
  OSLOGIN = ServiceDefinition(
      'oslogin', 'v1', 'https://oslogin.googleapis.com/$discovery/rest?version=v1')
  PAGESPEEDONLINE = ServiceDefinition(
      'pagespeedonline', 'v5', 'https://pagespeedonline.googleapis.com/$discovery/rest?version=v5')
  PARALLELSTORE = ServiceDefinition(
      'parallelstore', 'v1', 'https://parallelstore.googleapis.com/$discovery/rest?version=v1')
  PARAMETERMANAGER = ServiceDefinition(
      'parametermanager', 'v1', 'https://parametermanager.googleapis.com/$discovery/rest?version=v1')
  PAYMENTSRESELLERSUBSCRIPTION = ServiceDefinition(
      'paymentsresellersubscription', 'v1', 'https://paymentsresellersubscription.googleapis.com/$discovery/rest?version=v1')
  PEOPLE = ServiceDefinition(
      'people', 'v1', 'https://people.googleapis.com/$discovery/rest?version=v1')
  PLACES = ServiceDefinition(
      'places', 'v1', 'https://places.googleapis.com/$discovery/rest?version=v1')
  PLAYCUSTOMAPP = ServiceDefinition(
      'playcustomapp', 'v1', 'https://playcustomapp.googleapis.com/$discovery/rest?version=v1')
  PLAYDEVELOPERREPORTING = ServiceDefinition(
      'playdeveloperreporting', 'v1beta1', 'https://playdeveloperreporting.googleapis.com/$discovery/rest?version=v1beta1')
  PLAYGROUPING = ServiceDefinition(
      'playgrouping', 'v1alpha1', 'https://playgrouping.googleapis.com/$discovery/rest?version=v1alpha1')
  PLAYINTEGRITY = ServiceDefinition(
      'playintegrity', 'v1', 'https://playintegrity.googleapis.com/$discovery/rest?version=v1')
  POLICYANALYZER = ServiceDefinition(
      'policyanalyzer', 'v1', 'https://policyanalyzer.googleapis.com/$discovery/rest?version=v1')
  POLICYSIMULATOR = ServiceDefinition(
      'policysimulator', 'v1', 'https://policysimulator.googleapis.com/$discovery/rest?version=v1')
  POLICYTROUBLESHOOTER = ServiceDefinition(
      'policytroubleshooter', 'v1', 'https://policytroubleshooter.googleapis.com/$discovery/rest?version=v1')
  POLLEN = ServiceDefinition(
      'pollen', 'v1', 'https://pollen.googleapis.com/$discovery/rest?version=v1')
  POLY = ServiceDefinition(
      'poly', 'v1', 'https://poly.googleapis.com/$discovery/rest?version=v1')
  PRIVATECA = ServiceDefinition(
      'privateca', 'v1', 'https://privateca.googleapis.com/$discovery/rest?version=v1')
  PROD_TT_SASPORTAL = ServiceDefinition(
      'prod_tt_sasportal', 'v1alpha1', 'https://prod-tt-sasportal.googleapis.com/$discovery/rest?version=v1alpha1')
  PUBLICCA = ServiceDefinition(
      'publicca', 'v1', 'https://publicca.googleapis.com/$discovery/rest?version=v1')
  PUBSUB = ServiceDefinition(
      'pubsub', 'v1', 'https://pubsub.googleapis.com/$discovery/rest?version=v1')
  PUBSUBLITE = ServiceDefinition(
      'pubsublite', 'v1', 'https://pubsublite.googleapis.com/$discovery/rest?version=v1')
  RAPIDMIGRATIONASSESSMENT = ServiceDefinition(
      'rapidmigrationassessment', 'v1', 'https://rapidmigrationassessment.googleapis.com/$discovery/rest?version=v1')
  READERREVENUESUBSCRIPTIONLINKING = ServiceDefinition(
      'readerrevenuesubscriptionlinking', 'v1', 'https://readerrevenuesubscriptionlinking.googleapis.com/$discovery/rest?version=v1')
  REALTIMEBIDDING = ServiceDefinition(
      'realtimebidding', 'v1', 'https://realtimebidding.googleapis.com/$discovery/rest?version=v1')
  RECAPTCHAENTERPRISE = ServiceDefinition(
      'recaptchaenterprise', 'v1', 'https://recaptchaenterprise.googleapis.com/$discovery/rest?version=v1')
  RECOMMENDATIONENGINE = ServiceDefinition(
      'recommendationengine', 'v1beta1', 'https://recommendationengine.googleapis.com/$discovery/rest?version=v1beta1')
  RECOMMENDER = ServiceDefinition(
      'recommender', 'v1', 'https://recommender.googleapis.com/$discovery/rest?version=v1')
  REDIS = ServiceDefinition(
      'redis', 'v1', 'https://redis.googleapis.com/$discovery/rest?version=v1')
  RESELLER = ServiceDefinition(
      'reseller', 'v1', 'https://reseller.googleapis.com/$discovery/rest?version=v1')
  RETAIL = ServiceDefinition(
      'retail', 'v2', 'https://retail.googleapis.com/$discovery/rest?version=v2')
  RUN = ServiceDefinition(
      'run', 'v2', 'https://run.googleapis.com/$discovery/rest?version=v2')
  RUNTIMECONFIG = ServiceDefinition(
      'runtimeconfig', 'v1', 'https://runtimeconfig.googleapis.com/$discovery/rest?version=v1')
  SAASSERVICEMGMT = ServiceDefinition(
      'saasservicemgmt', 'v1beta1', 'https://saasservicemgmt.googleapis.com/$discovery/rest?version=v1beta1')
  SAFEBROWSING = ServiceDefinition(
      'safebrowsing', 'v5', 'https://safebrowsing.googleapis.com/$discovery/rest?version=v5')
  SASPORTAL = ServiceDefinition(
      'sasportal', 'v1alpha1', 'https://sasportal.googleapis.com/$discovery/rest?version=v1alpha1')
  SCRIPT = ServiceDefinition(
      'script', 'v1', 'https://script.googleapis.com/$discovery/rest?version=v1')
  SEARCHADS360 = ServiceDefinition(
      'searchads360', 'v0', 'https://searchads360.googleapis.com/$discovery/rest?version=v0')
  SEARCHCONSOLE = ServiceDefinition(
      'searchconsole', 'v1', 'https://searchconsole.googleapis.com/$discovery/rest?version=v1')
  SECRETMANAGER = ServiceDefinition(
      'secretmanager', 'v1', 'https://secretmanager.googleapis.com/$discovery/rest?version=v1')
  SECURITYCENTER = ServiceDefinition(
      'securitycenter', 'v1', 'https://securitycenter.googleapis.com/$discovery/rest?version=v1')
  SECURITYPOSTURE = ServiceDefinition(
      'securityposture', 'v1', 'https://securityposture.googleapis.com/$discovery/rest?version=v1')
  SERVICECONSUMERMANAGEMENT = ServiceDefinition(
      'serviceconsumermanagement', 'v1', 'https://serviceconsumermanagement.googleapis.com/$discovery/rest?version=v1')
  SERVICECONTROL = ServiceDefinition(
      'servicecontrol', 'v2', 'https://servicecontrol.googleapis.com/$discovery/rest?version=v2')
  SERVICEDIRECTORY = ServiceDefinition(
      'servicedirectory', 'v1', 'https://servicedirectory.googleapis.com/$discovery/rest?version=v1')
  SERVICEMANAGEMENT = ServiceDefinition(
      'servicemanagement', 'v1', 'https://servicemanagement.googleapis.com/$discovery/rest?version=v1')
  SERVICENETWORKING = ServiceDefinition(
      'servicenetworking', 'v1', 'https://servicenetworking.googleapis.com/$discovery/rest?version=v1')
  SERVICEUSAGE = ServiceDefinition(
      'serviceusage', 'v1', 'https://serviceusage.googleapis.com/$discovery/rest?version=v1')
  SHEETS = ServiceDefinition(
      'sheets', 'v4', 'https://sheets.googleapis.com/$discovery/rest?version=v4')
  SITEVERIFICATION = ServiceDefinition(
      'siteVerification', 'v1', 'https://siteverification.googleapis.com/$discovery/rest?version=v1')
  SLIDES = ServiceDefinition(
      'slides', 'v1', 'https://slides.googleapis.com/$discovery/rest?version=v1')
  SMARTDEVICEMANAGEMENT = ServiceDefinition(
      'smartdevicemanagement', 'v1', 'https://smartdevicemanagement.googleapis.com/$discovery/rest?version=v1')
  SOLAR = ServiceDefinition(
      'solar', 'v1', 'https://solar.googleapis.com/$discovery/rest?version=v1')
  SPANNER = ServiceDefinition(
      'spanner', 'v1', 'https://spanner.googleapis.com/$discovery/rest?version=v1')
  SPEECH = ServiceDefinition(
      'speech', 'v1', 'https://speech.googleapis.com/$discovery/rest?version=v1')
  SQLADMIN = ServiceDefinition(
      'sqladmin', 'v1', 'https://sqladmin.googleapis.com/$discovery/rest?version=v1')
  STORAGE = ServiceDefinition(
      'storage', 'v1', 'https://storage.googleapis.com/$discovery/rest?version=v1')
  STORAGEBATCHOPERATIONS = ServiceDefinition(
      'storagebatchoperations', 'v1', 'https://storagebatchoperations.googleapis.com/$discovery/rest?version=v1')
  STORAGETRANSFER = ServiceDefinition(
      'storagetransfer', 'v1', 'https://storagetransfer.googleapis.com/$discovery/rest?version=v1')
  STREETVIEWPUBLISH = ServiceDefinition(
      'streetviewpublish', 'v1', 'https://streetviewpublish.googleapis.com/$discovery/rest?version=v1')
  STS = ServiceDefinition(
      'sts', 'v1', 'https://sts.googleapis.com/$discovery/rest?version=v1')
  TAGMANAGER = ServiceDefinition(
      'tagmanager', 'v2', 'https://tagmanager.googleapis.com/$discovery/rest?version=v2')
  TASKS = ServiceDefinition(
      'tasks', 'v1', 'https://tasks.googleapis.com/$discovery/rest?version=v1')
  TESTING = ServiceDefinition(
      'testing', 'v1', 'https://testing.googleapis.com/$discovery/rest?version=v1')
  TEXTTOSPEECH = ServiceDefinition(
      'texttospeech', 'v1', 'https://texttospeech.googleapis.com/$discovery/rest?version=v1')
  TOOLRESULTS = ServiceDefinition(
      'toolresults', 'v1beta3', 'https://toolresults.googleapis.com/$discovery/rest?version=v1beta3')
  TPU = ServiceDefinition(
      'tpu', 'v2', 'https://tpu.googleapis.com/$discovery/rest?version=v2')
  TRAFFICDIRECTOR = ServiceDefinition(
      'trafficdirector', 'v3', 'https://trafficdirector.googleapis.com/$discovery/rest?version=v3')
  TRANSCODER = ServiceDefinition(
      'transcoder', 'v1', 'https://transcoder.googleapis.com/$discovery/rest?version=v1')
  TRANSLATE = ServiceDefinition(
      'translate', 'v3', 'https://translation.googleapis.com/$discovery/rest?version=v3')
  TRAVELIMPACTMODEL = ServiceDefinition(
      'travelimpactmodel', 'v1', 'https://travelimpactmodel.googleapis.com/$discovery/rest?version=v1')
  VAULT = ServiceDefinition(
      'vault', 'v1', 'https://vault.googleapis.com/$discovery/rest?version=v1')
  VERIFIEDACCESS = ServiceDefinition(
      'verifiedaccess', 'v2', 'https://verifiedaccess.googleapis.com/$discovery/rest?version=v2')
  VERSIONHISTORY = ServiceDefinition(
      'versionhistory', 'v1', 'https://versionhistory.googleapis.com/$discovery/rest?version=v1')
  VIDEOINTELLIGENCE = ServiceDefinition(
      'videointelligence', 'v1', 'https://videointelligence.googleapis.com/$discovery/rest?version=v1')
  VISION = ServiceDefinition(
      'vision', 'v1', 'https://vision.googleapis.com/$discovery/rest?version=v1')
  VMMIGRATION = ServiceDefinition(
      'vmmigration', 'v1', 'https://vmmigration.googleapis.com/$discovery/rest?version=v1')
  VMWAREENGINE = ServiceDefinition(
      'vmwareengine', 'v1', 'https://vmwareengine.googleapis.com/$discovery/rest?version=v1')
  VPCACCESS = ServiceDefinition(
      'vpcaccess', 'v1', 'https://vpcaccess.googleapis.com/$discovery/rest?version=v1')
  WALLETOBJECTS = ServiceDefinition(
      'walletobjects', 'v1', 'https://walletobjects.googleapis.com/$discovery/rest?version=v1')
  WEBFONTS = ServiceDefinition(
      'webfonts', 'v1', 'https://webfonts.googleapis.com/$discovery/rest?version=v1')
  WEBRISK = ServiceDefinition(
      'webrisk', 'v1', 'https://webrisk.googleapis.com/$discovery/rest?version=v1')
  WEBSECURITYSCANNER = ServiceDefinition(
      'websecurityscanner', 'v1', 'https://websecurityscanner.googleapis.com/$discovery/rest?version=v1')
  WORKFLOWEXECUTIONS = ServiceDefinition(
      'workflowexecutions', 'v1', 'https://workflowexecutions.googleapis.com/$discovery/rest?version=v1')
  WORKFLOWS = ServiceDefinition(
      'workflows', 'v1', 'https://workflows.googleapis.com/$discovery/rest?version=v1')
  WORKLOADMANAGER = ServiceDefinition(
      'workloadmanager', 'v1', 'https://workloadmanager.googleapis.com/$discovery/rest?version=v1')
  WORKSPACEEVENTS = ServiceDefinition(
      'workspaceevents', 'v1', 'https://workspaceevents.googleapis.com/$discovery/rest?version=v1')
  WORKSTATIONS = ServiceDefinition(
      'workstations', 'v1', 'https://workstations.googleapis.com/$discovery/rest?version=v1')
  YOUTUBE = ServiceDefinition(
      'youtube', 'v3', 'https://youtube.googleapis.com/$discovery/rest?version=v3')
  YOUTUBEANALYTICS = ServiceDefinition(
      'youtubeAnalytics', 'v2', 'https://youtubeanalytics.googleapis.com/$discovery/rest?version=v2')
  YOUTUBEREPORTING = ServiceDefinition(
      'youtubereporting', 'v1', 'https://youtubereporting.googleapis.com/$discovery/rest?version=v1')
