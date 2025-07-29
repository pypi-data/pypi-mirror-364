======
README
======

The source files used for generate the vocabulary and translation locaes are
taken from the debian iso codes files form the public ftp server:
http://pkg-isocodes.alioth.debian.org/downloads/

This files are licenced as LGPL

If you need to update to the newest source, download the newest source files
and copy the iso_3166 folder to the source folder in this package. After that
you can run the ``extract``buildout script with bin/extract. This will generate
the requiredvocabulary csv source files, copy the *.po files to the right
LC_MESSAGES folders and generate the *.mo files. Note; this will require a
working msgfmt script installation.

For more information about the ISO 3166-1 standard see the following resources:

http://en.wikipedia.org/wiki/ISO_3166-2

http://en.wikipedia.org/wiki/ISO_3166-1_alpha-2


ISO3166Alpha2CountryVocabulary
------------------------------

This is a country vocabulary uses the ``ISO 3166 ALPHA-2 code`` country codes.

Let's test the country vocabulary.

  >>> from __future__ import absolute_import, print_function
  >>> from pprint import pprint
  >>> import p01.vocabulary.country
  >>> vocab = p01.vocabulary.country.ISO3166Alpha2CountryVocabulary(None)
  >>> len(vocab)
  250

  >>> for item in vocab:
  ...     print('%s %s %s' % (item.value, item.token, item.title))
  AF AF Afghanistan
  AX AX Åland Islands
  AL AL Albania
  DZ DZ Algeria
  AS AS American Samoa
  AD AD Andorra
  AO AO Angola
  AI AI Anguilla
  AQ AQ Antarctica
  AG AG Antigua and Barbuda
  AR AR Argentina
  AM AM Armenia
  AW AW Aruba
  AU AU Australia
  AT AT Austria
  AZ AZ Azerbaijan
  BS BS Bahamas
  BH BH Bahrain
  BD BD Bangladesh
  BB BB Barbados
  BY BY Belarus
  BE BE Belgium
  BZ BZ Belize
  BJ BJ Benin
  BM BM Bermuda
  BT BT Bhutan
  BO BO Bolivia
  BQ BQ Bonaire, Sint Eustatius and Saba
  BA BA Bosnia and Herzegovina
  BW BW Botswana
  BV BV Bouvet Island
  BR BR Brazil
  IO IO British Indian Ocean Territory
  BN BN Brunei Darussalam
  BG BG Bulgaria
  BF BF Burkina Faso
  BI BI Burundi
  KH KH Cambodia
  CM CM Cameroon
  CA CA Canada
  CV CV Cape Verde
  KY KY Cayman Islands
  CF CF Central African Republic
  TD TD Chad
  CL CL Chile
  CN CN China
  CX CX Christmas Island
  CC CC Cocos (Keeling) Islands
  CO CO Colombia
  KM KM Comoros
  CG CG Congo
  CD CD Congo, The Democratic Republic of the
  CK CK Cook Islands
  CR CR Costa Rica
  CI CI Côte d'Ivoire
  HR HR Croatia
  CU CU Cuba
  CW CW Cura\xe7ao
  CY CY Cyprus
  CZ CZ Czech Republic
  DK DK Denmark
  DJ DJ Djibouti
  DM DM Dominica
  DO DO Dominican Republic
  EC EC Ecuador
  EG EG Egypt
  SV SV El Salvador
  GQ GQ Equatorial Guinea
  ER ER Eritrea
  EE EE Estonia
  ET ET Ethiopia
  FK FK Falkland Islands (Malvinas)
  FO FO Faroe Islands
  FJ FJ Fiji
  FI FI Finland
  FR FR France
  GF GF French Guiana
  PF PF French Polynesia
  TF TF French Southern Territories
  GA GA Gabon
  GM GM Gambia
  GE GE Georgia
  DE DE Germany
  GH GH Ghana
  GI GI Gibraltar
  GR GR Greece
  GL GL Greenland
  GD GD Grenada
  GP GP Guadeloupe
  GU GU Guam
  GT GT Guatemala
  GG GG Guernsey
  GN GN Guinea
  GW GW Guinea-Bissau
  GY GY Guyana
  HT HT Haiti
  HM HM Heard Island and McDonald Islands
  VA VA Holy See (Vatican City State)
  HN HN Honduras
  HK HK Hong Kong
  HU HU Hungary
  IS IS Iceland
  IN IN India
  ID ID Indonesia
  IR IR Iran, Islamic Republic of
  IQ IQ Iraq
  IE IE Ireland
  IM IM Isle of Man
  IL IL Israel
  IT IT Italy
  JM JM Jamaica
  JP JP Japan
  JE JE Jersey
  JO JO Jordan
  KZ KZ Kazakhstan
  KE KE Kenya
  KI KI Kiribati
  KP KP Korea, Democratic People's Republic of
  KR KR Korea, Republic of
  KW KW Kuwait
  KG KG Kyrgyzstan
  LA LA Lao People's Democratic Republic
  LV LV Latvia
  LB LB Lebanon
  LS LS Lesotho
  LR LR Liberia
  LY LY Libya
  LI LI Liechtenstein
  LT LT Lithuania
  LU LU Luxembourg
  MO MO Macao
  MK MK Macedonia, Republic of
  MG MG Madagascar
  MW MW Malawi
  MY MY Malaysia
  MV MV Maldives
  ML ML Mali
  MT MT Malta
  MH MH Marshall Islands
  MQ MQ Martinique
  MR MR Mauritania
  MU MU Mauritius
  YT YT Mayotte
  MX MX Mexico
  FM FM Micronesia, Federated States of
  MD MD Moldova
  MC MC Monaco
  MN MN Mongolia
  ME ME Montenegro
  MS MS Montserrat
  MA MA Morocco
  MZ MZ Mozambique
  MM MM Myanmar
  NA NA Namibia
  NR NR Nauru
  NP NP Nepal
  NL NL Netherlands
  NC NC New Caledonia
  NZ NZ New Zealand
  NI NI Nicaragua
  NE NE Niger
  NG NG Nigeria
  NU NU Niue
  NF NF Norfolk Island
  MP MP Northern Mariana Islands
  NO NO Norway
  OM OM Oman
  PK PK Pakistan
  PW PW Palau
  PS PS Palestinian Territory, Occupied
  PA PA Panama
  PG PG Papua New Guinea
  PY PY Paraguay
  PE PE Peru
  PH PH Philippines
  PN PN Pitcairn
  PL PL Poland
  PT PT Portugal
  PR PR Puerto Rico
  QA QA Qatar
  RE RE R\xe9union
  RO RO Romania
  RU RU Russian Federation
  RW RW Rwanda
  BL BL Saint Barth\xe9lemy
  SH SH Saint Helena, Ascension and Tristan da Cunha
  KN KN Saint Kitts and Nevis
  LC LC Saint Lucia
  MF MF Saint Martin (French part)
  PM PM Saint Pierre and Miquelon
  VC VC Saint Vincent and the Grenadines
  WS WS Samoa
  SM SM San Marino
  ST ST Sao Tome and Principe
  SA SA Saudi Arabia
  SN SN Senegal
  RS RS Serbia
  SC SC Seychelles
  SL SL Sierra Leone
  SG SG Singapore
  SX SX Sint Maarten (Dutch part)
  SK SK Slovakia
  SI SI Slovenia
  SB SB Solomon Islands
  SO SO Somalia
  ZA ZA South Africa
  GS GS South Georgia and the South Sandwich Islands
  ES ES Spain
  LK LK Sri Lanka
  SD SD Sudan
  SR SR Suriname
  SS SS South Sudan
  SJ SJ Svalbard and Jan Mayen
  SZ SZ Swaziland
  SE SE Sweden
  CH CH Switzerland
  SY SY Syrian Arab Republic
  TW TW Taiwan
  TJ TJ Tajikistan
  TZ TZ Tanzania, United Republic of
  TH TH Thailand
  TL TL Timor-Leste
  TG TG Togo
  TK TK Tokelau
  TO TO Tonga
  TT TT Trinidad and Tobago
  TN TN Tunisia
  TR TR Turkey
  TM TM Turkmenistan
  TC TC Turks and Caicos Islands
  TV TV Tuvalu
  UG UG Uganda
  UA UA Ukraine
  AE AE United Arab Emirates
  GB GB United Kingdom
  US US United States
  UM UM United States Minor Outlying Islands
  UY UY Uruguay
  UZ UZ Uzbekistan
  VU VU Vanuatu
  VE VE Venezuela
  VN VN Viet Nam
  VG VG Virgin Islands, British
  VI VI Virgin Islands, U.S.
  WF WF Wallis and Futuna
  EH EH Western Sahara
  YE YE Yemen
  ZM ZM Zambia
  ZW ZW Zimbabwe
  XK XK Kosovo

The vocabulary allow us to get a term by token:

  >>> term = vocab.getTermByToken('CH')
  >>> term
  <zope.schema.vocabulary.SimpleTerm object at ...>

  >>> term.token
  'CH'

  >>> print(term.value)
  CH

  >>> print(term.title)
  Switzerland

Or we can get a term by value:

  >>> term = vocab.getTerm('CH')
  >>> term
  <zope.schema.vocabulary.SimpleTerm object at ...>

  >>> term.token
  'CH'

  >>> print(term.value)
  CH

  >>> print(term.title)
  Switzerland


ISO3166Alpha3CountryVocabulary
------------------------------

This is a country vocabulary uses the ``ISO 3166 ALPHA-3 code`` country codes.

Let's test the country vocabulary.

  >>> vocab = p01.vocabulary.country.ISO3166Alpha3CountryVocabulary(None)
  >>> len(vocab)
  250

  >>> for item in vocab:
  ...     print('%s %s %s' % (item.value, item.token, item.title))
  AFG AFG Afghanistan
  ALA ALA Åland Islands
  ALB ALB Albania
  DZA DZA Algeria
  ASM ASM American Samoa
  AND AND Andorra
  AGO AGO Angola
  AIA AIA Anguilla
  ATA ATA Antarctica
  ATG ATG Antigua and Barbuda
  ARG ARG Argentina
  ARM ARM Armenia
  ABW ABW Aruba
  AUS AUS Australia
  AUT AUT Austria
  AZE AZE Azerbaijan
  BHS BHS Bahamas
  BHR BHR Bahrain
  BGD BGD Bangladesh
  BRB BRB Barbados
  BLR BLR Belarus
  BEL BEL Belgium
  BLZ BLZ Belize
  BEN BEN Benin
  BMU BMU Bermuda
  BTN BTN Bhutan
  BOL BOL Bolivia
  BES BES Bonaire, Sint Eustatius and Saba
  BIH BIH Bosnia and Herzegovina
  BWA BWA Botswana
  BVT BVT Bouvet Island
  BRA BRA Brazil
  IOT IOT British Indian Ocean Territory
  BRN BRN Brunei Darussalam
  BGR BGR Bulgaria
  BFA BFA Burkina Faso
  BDI BDI Burundi
  KHM KHM Cambodia
  CMR CMR Cameroon
  CAN CAN Canada
  CPV CPV Cape Verde
  CYM CYM Cayman Islands
  CAF CAF Central African Republic
  TCD TCD Chad
  CHL CHL Chile
  CHN CHN China
  CXR CXR Christmas Island
  CCK CCK Cocos (Keeling) Islands
  COL COL Colombia
  COM COM Comoros
  COG COG Congo
  COD COD Congo, The Democratic Republic of the
  COK COK Cook Islands
  CRI CRI Costa Rica
  CIV CIV Côte d'Ivoire
  HRV HRV Croatia
  CUB CUB Cuba
  CUW CUW Cura\xe7ao
  CYP CYP Cyprus
  CZE CZE Czech Republic
  DNK DNK Denmark
  DJI DJI Djibouti
  DMA DMA Dominica
  DOM DOM Dominican Republic
  ECU ECU Ecuador
  EGY EGY Egypt
  SLV SLV El Salvador
  GNQ GNQ Equatorial Guinea
  ERI ERI Eritrea
  EST EST Estonia
  ETH ETH Ethiopia
  FLK FLK Falkland Islands (Malvinas)
  FRO FRO Faroe Islands
  FJI FJI Fiji
  FIN FIN Finland
  FRA FRA France
  GUF GUF French Guiana
  PYF PYF French Polynesia
  ATF ATF French Southern Territories
  GAB GAB Gabon
  GMB GMB Gambia
  GEO GEO Georgia
  DEU DEU Germany
  GHA GHA Ghana
  GIB GIB Gibraltar
  GRC GRC Greece
  GRL GRL Greenland
  GRD GRD Grenada
  GLP GLP Guadeloupe
  GUM GUM Guam
  GTM GTM Guatemala
  GGY GGY Guernsey
  GIN GIN Guinea
  GNB GNB Guinea-Bissau
  GUY GUY Guyana
  HTI HTI Haiti
  HMD HMD Heard Island and McDonald Islands
  VAT VAT Holy See (Vatican City State)
  HND HND Honduras
  HKG HKG Hong Kong
  HUN HUN Hungary
  ISL ISL Iceland
  IND IND India
  IDN IDN Indonesia
  IRN IRN Iran, Islamic Republic of
  IRQ IRQ Iraq
  IRL IRL Ireland
  IMN IMN Isle of Man
  ISR ISR Israel
  ITA ITA Italy
  JAM JAM Jamaica
  JPN JPN Japan
  JEY JEY Jersey
  JOR JOR Jordan
  KAZ KAZ Kazakhstan
  KEN KEN Kenya
  KIR KIR Kiribati
  PRK PRK Korea, Democratic People's Republic of
  KOR KOR Korea, Republic of
  KWT KWT Kuwait
  KGZ KGZ Kyrgyzstan
  LAO LAO Lao People's Democratic Republic
  LVA LVA Latvia
  LBN LBN Lebanon
  LSO LSO Lesotho
  LBR LBR Liberia
  LBY LBY Libya
  LIE LIE Liechtenstein
  LTU LTU Lithuania
  LUX LUX Luxembourg
  MAC MAC Macao
  MKD MKD Macedonia, Republic of
  MDG MDG Madagascar
  MWI MWI Malawi
  MYS MYS Malaysia
  MDV MDV Maldives
  MLI MLI Mali
  MLT MLT Malta
  MHL MHL Marshall Islands
  MTQ MTQ Martinique
  MRT MRT Mauritania
  MUS MUS Mauritius
  MYT MYT Mayotte
  MEX MEX Mexico
  FSM FSM Micronesia, Federated States of
  MDA MDA Moldova
  MCO MCO Monaco
  MNG MNG Mongolia
  MNE MNE Montenegro
  MSR MSR Montserrat
  MAR MAR Morocco
  MOZ MOZ Mozambique
  MMR MMR Myanmar
  NAM NAM Namibia
  NRU NRU Nauru
  NPL NPL Nepal
  NLD NLD Netherlands
  NCL NCL New Caledonia
  NZL NZL New Zealand
  NIC NIC Nicaragua
  NER NER Niger
  NGA NGA Nigeria
  NIU NIU Niue
  NFK NFK Norfolk Island
  MNP MNP Northern Mariana Islands
  NOR NOR Norway
  OMN OMN Oman
  PAK PAK Pakistan
  PLW PLW Palau
  PSE PSE Palestinian Territory, Occupied
  PAN PAN Panama
  PNG PNG Papua New Guinea
  PRY PRY Paraguay
  PER PER Peru
  PHL PHL Philippines
  PCN PCN Pitcairn
  POL POL Poland
  PRT PRT Portugal
  PRI PRI Puerto Rico
  QAT QAT Qatar
  REU REU R\xe9union
  ROU ROU Romania
  RUS RUS Russian Federation
  RWA RWA Rwanda
  BLM BLM Saint Barth\xe9lemy
  SHN SHN Saint Helena, Ascension and Tristan da Cunha
  KNA KNA Saint Kitts and Nevis
  LCA LCA Saint Lucia
  MAF MAF Saint Martin (French part)
  SPM SPM Saint Pierre and Miquelon
  VCT VCT Saint Vincent and the Grenadines
  WSM WSM Samoa
  SMR SMR San Marino
  STP STP Sao Tome and Principe
  SAU SAU Saudi Arabia
  SEN SEN Senegal
  SRB SRB Serbia
  SYC SYC Seychelles
  SLE SLE Sierra Leone
  SGP SGP Singapore
  SXM SXM Sint Maarten (Dutch part)
  SVK SVK Slovakia
  SVN SVN Slovenia
  SLB SLB Solomon Islands
  SOM SOM Somalia
  ZAF ZAF South Africa
  SGS SGS South Georgia and the South Sandwich Islands
  ESP ESP Spain
  LKA LKA Sri Lanka
  SDN SDN Sudan
  SUR SUR Suriname
  SSD SSD South Sudan
  SJM SJM Svalbard and Jan Mayen
  SWZ SWZ Swaziland
  SWE SWE Sweden
  CHE CHE Switzerland
  SYR SYR Syrian Arab Republic
  TWN TWN Taiwan
  TJK TJK Tajikistan
  TZA TZA Tanzania, United Republic of
  THA THA Thailand
  TLS TLS Timor-Leste
  TGO TGO Togo
  TKL TKL Tokelau
  TON TON Tonga
  TTO TTO Trinidad and Tobago
  TUN TUN Tunisia
  TUR TUR Turkey
  TKM TKM Turkmenistan
  TCA TCA Turks and Caicos Islands
  TUV TUV Tuvalu
  UGA UGA Uganda
  UKR UKR Ukraine
  ARE ARE United Arab Emirates
  GBR GBR United Kingdom
  USA USA United States
  UMI UMI United States Minor Outlying Islands
  URY URY Uruguay
  UZB UZB Uzbekistan
  VUT VUT Vanuatu
  VEN VEN Venezuela
  VNM VNM Viet Nam
  VGB VGB Virgin Islands, British
  VIR VIR Virgin Islands, U.S.
  WLF WLF Wallis and Futuna
  ESH ESH Western Sahara
  YEM YEM Yemen
  ZMB ZMB Zambia
  ZWE ZWE Zimbabwe
  XKV XKV Kosovo

The vocabulary allow us to get a term by token:

  >>> term = vocab.getTermByToken('CHE')
  >>> term
  <zope.schema.vocabulary.SimpleTerm object at ...>

  >>> term.token
  'CHE'

  >>> print(term.value)
  CHE

  >>> print(term.title)
  Switzerland

Or we can get a term by value:

  >>> term = vocab.getTerm('CHE')
  >>> term
  <zope.schema.vocabulary.SimpleTerm object at ...>

  >>> term.token
  'CHE'

  >>> print(term.value)
  CHE

  >>> print(term.title)
  Switzerland


alpha2to3
---------

  >>> from p01.vocabulary.country import alpha2to3
  >>> pprint(alpha2to3)
  {'AD': 'AND',
   'AE': 'ARE',
   'AF': 'AFG',
   'AG': 'ATG',
   'AI': 'AIA',
   'AL': 'ALB',
   'AM': 'ARM',
   'AO': 'AGO',
   'AQ': 'ATA',
   'AR': 'ARG',
   'AS': 'ASM',
   'AT': 'AUT',
   'AU': 'AUS',
   'AW': 'ABW',
   'AX': 'ALA',
   'AZ': 'AZE',
   'BA': 'BIH',
   'BB': 'BRB',
   'BD': 'BGD',
   'BE': 'BEL',
   'BF': 'BFA',
   'BG': 'BGR',
   'BH': 'BHR',
   'BI': 'BDI',
   'BJ': 'BEN',
   'BL': 'BLM',
   'BM': 'BMU',
   'BN': 'BRN',
   'BO': 'BOL',
   'BQ': 'BES',
   'BR': 'BRA',
   'BS': 'BHS',
   'BT': 'BTN',
   'BV': 'BVT',
   'BW': 'BWA',
   'BY': 'BLR',
   'BZ': 'BLZ',
   'CA': 'CAN',
   'CC': 'CCK',
   'CD': 'COD',
   'CF': 'CAF',
   'CG': 'COG',
   'CH': 'CHE',
   'CI': 'CIV',
   'CK': 'COK',
   'CL': 'CHL',
   'CM': 'CMR',
   'CN': 'CHN',
   'CO': 'COL',
   'CR': 'CRI',
   'CU': 'CUB',
   'CV': 'CPV',
   'CW': 'CUW',
   'CX': 'CXR',
   'CY': 'CYP',
   'CZ': 'CZE',
   'DE': 'DEU',
   'DJ': 'DJI',
   'DK': 'DNK',
   'DM': 'DMA',
   'DO': 'DOM',
   'DZ': 'DZA',
   'EC': 'ECU',
   'EE': 'EST',
   'EG': 'EGY',
   'EH': 'ESH',
   'ER': 'ERI',
   'ES': 'ESP',
   'ET': 'ETH',
   'FI': 'FIN',
   'FJ': 'FJI',
   'FK': 'FLK',
   'FM': 'FSM',
   'FO': 'FRO',
   'FR': 'FRA',
   'GA': 'GAB',
   'GB': 'GBR',
   'GD': 'GRD',
   'GE': 'GEO',
   'GF': 'GUF',
   'GG': 'GGY',
   'GH': 'GHA',
   'GI': 'GIB',
   'GL': 'GRL',
   'GM': 'GMB',
   'GN': 'GIN',
   'GP': 'GLP',
   'GQ': 'GNQ',
   'GR': 'GRC',
   'GS': 'SGS',
   'GT': 'GTM',
   'GU': 'GUM',
   'GW': 'GNB',
   'GY': 'GUY',
   'HK': 'HKG',
   'HM': 'HMD',
   'HN': 'HND',
   'HR': 'HRV',
   'HT': 'HTI',
   'HU': 'HUN',
   'ID': 'IDN',
   'IE': 'IRL',
   'IL': 'ISR',
   'IM': 'IMN',
   'IN': 'IND',
   'IO': 'IOT',
   'IQ': 'IRQ',
   'IR': 'IRN',
   'IS': 'ISL',
   'IT': 'ITA',
   'JE': 'JEY',
   'JM': 'JAM',
   'JO': 'JOR',
   'JP': 'JPN',
   'KE': 'KEN',
   'KG': 'KGZ',
   'KH': 'KHM',
   'KI': 'KIR',
   'KM': 'COM',
   'KN': 'KNA',
   'KP': 'PRK',
   'KR': 'KOR',
   'KW': 'KWT',
   'KY': 'CYM',
   'KZ': 'KAZ',
   'LA': 'LAO',
   'LB': 'LBN',
   'LC': 'LCA',
   'LI': 'LIE',
   'LK': 'LKA',
   'LR': 'LBR',
   'LS': 'LSO',
   'LT': 'LTU',
   'LU': 'LUX',
   'LV': 'LVA',
   'LY': 'LBY',
   'MA': 'MAR',
   'MC': 'MCO',
   'MD': 'MDA',
   'ME': 'MNE',
   'MF': 'MAF',
   'MG': 'MDG',
   'MH': 'MHL',
   'MK': 'MKD',
   'ML': 'MLI',
   'MM': 'MMR',
   'MN': 'MNG',
   'MO': 'MAC',
   'MP': 'MNP',
   'MQ': 'MTQ',
   'MR': 'MRT',
   'MS': 'MSR',
   'MT': 'MLT',
   'MU': 'MUS',
   'MV': 'MDV',
   'MW': 'MWI',
   'MX': 'MEX',
   'MY': 'MYS',
   'MZ': 'MOZ',
   'NA': 'NAM',
   'NC': 'NCL',
   'NE': 'NER',
   'NF': 'NFK',
   'NG': 'NGA',
   'NI': 'NIC',
   'NL': 'NLD',
   'NO': 'NOR',
   'NP': 'NPL',
   'NR': 'NRU',
   'NU': 'NIU',
   'NZ': 'NZL',
   'OM': 'OMN',
   'PA': 'PAN',
   'PE': 'PER',
   'PF': 'PYF',
   'PG': 'PNG',
   'PH': 'PHL',
   'PK': 'PAK',
   'PL': 'POL',
   'PM': 'SPM',
   'PN': 'PCN',
   'PR': 'PRI',
   'PS': 'PSE',
   'PT': 'PRT',
   'PW': 'PLW',
   'PY': 'PRY',
   'QA': 'QAT',
   'RE': 'REU',
   'RO': 'ROU',
   'RS': 'SRB',
   'RU': 'RUS',
   'RW': 'RWA',
   'SA': 'SAU',
   'SB': 'SLB',
   'SC': 'SYC',
   'SD': 'SDN',
   'SE': 'SWE',
   'SG': 'SGP',
   'SH': 'SHN',
   'SI': 'SVN',
   'SJ': 'SJM',
   'SK': 'SVK',
   'SL': 'SLE',
   'SM': 'SMR',
   'SN': 'SEN',
   'SO': 'SOM',
   'SR': 'SUR',
   'SS': 'SSD',
   'ST': 'STP',
   'SV': 'SLV',
   'SX': 'SXM',
   'SY': 'SYR',
   'SZ': 'SWZ',
   'TC': 'TCA',
   'TD': 'TCD',
   'TF': 'ATF',
   'TG': 'TGO',
   'TH': 'THA',
   'TJ': 'TJK',
   'TK': 'TKL',
   'TL': 'TLS',
   'TM': 'TKM',
   'TN': 'TUN',
   'TO': 'TON',
   'TR': 'TUR',
   'TT': 'TTO',
   'TV': 'TUV',
   'TW': 'TWN',
   'TZ': 'TZA',
   'UA': 'UKR',
   'UG': 'UGA',
   'UM': 'UMI',
   'US': 'USA',
   'UY': 'URY',
   'UZ': 'UZB',
   'VA': 'VAT',
   'VC': 'VCT',
   'VE': 'VEN',
   'VG': 'VGB',
   'VI': 'VIR',
   'VN': 'VNM',
   'VU': 'VUT',
   'WF': 'WLF',
   'WS': 'WSM',
   'XK': 'XKV',
   'YE': 'YEM',
   'YT': 'MYT',
   'ZA': 'ZAF',
   'ZM': 'ZMB',
   'ZW': 'ZWE'}

alpha3to2
---------

  >>> from p01.vocabulary.country import alpha3to2
  >>> pprint(alpha3to2)
  {'ABW': 'AW',
   'AFG': 'AF',
   'AGO': 'AO',
   'AIA': 'AI',
   'ALA': 'AX',
   'ALB': 'AL',
   'AND': 'AD',
   'ARE': 'AE',
   'ARG': 'AR',
   'ARM': 'AM',
   'ASM': 'AS',
   'ATA': 'AQ',
   'ATF': 'TF',
   'ATG': 'AG',
   'AUS': 'AU',
   'AUT': 'AT',
   'AZE': 'AZ',
   'BDI': 'BI',
   'BEL': 'BE',
   'BEN': 'BJ',
   'BES': 'BQ',
   'BFA': 'BF',
   'BGD': 'BD',
   'BGR': 'BG',
   'BHR': 'BH',
   'BHS': 'BS',
   'BIH': 'BA',
   'BLM': 'BL',
   'BLR': 'BY',
   'BLZ': 'BZ',
   'BMU': 'BM',
   'BOL': 'BO',
   'BRA': 'BR',
   'BRB': 'BB',
   'BRN': 'BN',
   'BTN': 'BT',
   'BVT': 'BV',
   'BWA': 'BW',
   'CAF': 'CF',
   'CAN': 'CA',
   'CCK': 'CC',
   'CHE': 'CH',
   'CHL': 'CL',
   'CHN': 'CN',
   'CIV': 'CI',
   'CMR': 'CM',
   'COD': 'CD',
   'COG': 'CG',
   'COK': 'CK',
   'COL': 'CO',
   'COM': 'KM',
   'CPV': 'CV',
   'CRI': 'CR',
   'CUB': 'CU',
   'CUW': 'CW',
   'CXR': 'CX',
   'CYM': 'KY',
   'CYP': 'CY',
   'CZE': 'CZ',
   'DEU': 'DE',
   'DJI': 'DJ',
   'DMA': 'DM',
   'DNK': 'DK',
   'DOM': 'DO',
   'DZA': 'DZ',
   'ECU': 'EC',
   'EGY': 'EG',
   'ERI': 'ER',
   'ESH': 'EH',
   'ESP': 'ES',
   'EST': 'EE',
   'ETH': 'ET',
   'FIN': 'FI',
   'FJI': 'FJ',
   'FLK': 'FK',
   'FRA': 'FR',
   'FRO': 'FO',
   'FSM': 'FM',
   'GAB': 'GA',
   'GBR': 'GB',
   'GEO': 'GE',
   'GGY': 'GG',
   'GHA': 'GH',
   'GIB': 'GI',
   'GIN': 'GN',
   'GLP': 'GP',
   'GMB': 'GM',
   'GNB': 'GW',
   'GNQ': 'GQ',
   'GRC': 'GR',
   'GRD': 'GD',
   'GRL': 'GL',
   'GTM': 'GT',
   'GUF': 'GF',
   'GUM': 'GU',
   'GUY': 'GY',
   'HKG': 'HK',
   'HMD': 'HM',
   'HND': 'HN',
   'HRV': 'HR',
   'HTI': 'HT',
   'HUN': 'HU',
   'IDN': 'ID',
   'IMN': 'IM',
   'IND': 'IN',
   'IOT': 'IO',
   'IRL': 'IE',
   'IRN': 'IR',
   'IRQ': 'IQ',
   'ISL': 'IS',
   'ISR': 'IL',
   'ITA': 'IT',
   'JAM': 'JM',
   'JEY': 'JE',
   'JOR': 'JO',
   'JPN': 'JP',
   'KAZ': 'KZ',
   'KEN': 'KE',
   'KGZ': 'KG',
   'KHM': 'KH',
   'KIR': 'KI',
   'KNA': 'KN',
   'KOR': 'KR',
   'KWT': 'KW',
   'LAO': 'LA',
   'LBN': 'LB',
   'LBR': 'LR',
   'LBY': 'LY',
   'LCA': 'LC',
   'LIE': 'LI',
   'LKA': 'LK',
   'LSO': 'LS',
   'LTU': 'LT',
   'LUX': 'LU',
   'LVA': 'LV',
   'MAC': 'MO',
   'MAF': 'MF',
   'MAR': 'MA',
   'MCO': 'MC',
   'MDA': 'MD',
   'MDG': 'MG',
   'MDV': 'MV',
   'MEX': 'MX',
   'MHL': 'MH',
   'MKD': 'MK',
   'MLI': 'ML',
   'MLT': 'MT',
   'MMR': 'MM',
   'MNE': 'ME',
   'MNG': 'MN',
   'MNP': 'MP',
   'MOZ': 'MZ',
   'MRT': 'MR',
   'MSR': 'MS',
   'MTQ': 'MQ',
   'MUS': 'MU',
   'MWI': 'MW',
   'MYS': 'MY',
   'MYT': 'YT',
   'NAM': 'NA',
   'NCL': 'NC',
   'NER': 'NE',
   'NFK': 'NF',
   'NGA': 'NG',
   'NIC': 'NI',
   'NIU': 'NU',
   'NLD': 'NL',
   'NOR': 'NO',
   'NPL': 'NP',
   'NRU': 'NR',
   'NZL': 'NZ',
   'OMN': 'OM',
   'PAK': 'PK',
   'PAN': 'PA',
   'PCN': 'PN',
   'PER': 'PE',
   'PHL': 'PH',
   'PLW': 'PW',
   'PNG': 'PG',
   'POL': 'PL',
   'PRI': 'PR',
   'PRK': 'KP',
   'PRT': 'PT',
   'PRY': 'PY',
   'PSE': 'PS',
   'PYF': 'PF',
   'QAT': 'QA',
   'REU': 'RE',
   'ROU': 'RO',
   'RUS': 'RU',
   'RWA': 'RW',
   'SAU': 'SA',
   'SDN': 'SD',
   'SEN': 'SN',
   'SGP': 'SG',
   'SGS': 'GS',
   'SHN': 'SH',
   'SJM': 'SJ',
   'SLB': 'SB',
   'SLE': 'SL',
   'SLV': 'SV',
   'SMR': 'SM',
   'SOM': 'SO',
   'SPM': 'PM',
   'SRB': 'RS',
   'SSD': 'SS',
   'STP': 'ST',
   'SUR': 'SR',
   'SVK': 'SK',
   'SVN': 'SI',
   'SWE': 'SE',
   'SWZ': 'SZ',
   'SXM': 'SX',
   'SYC': 'SC',
   'SYR': 'SY',
   'TCA': 'TC',
   'TCD': 'TD',
   'TGO': 'TG',
   'THA': 'TH',
   'TJK': 'TJ',
   'TKL': 'TK',
   'TKM': 'TM',
   'TLS': 'TL',
   'TON': 'TO',
   'TTO': 'TT',
   'TUN': 'TN',
   'TUR': 'TR',
   'TUV': 'TV',
   'TWN': 'TW',
   'TZA': 'TZ',
   'UGA': 'UG',
   'UKR': 'UA',
   'UMI': 'UM',
   'URY': 'UY',
   'USA': 'US',
   'UZB': 'UZ',
   'VAT': 'VA',
   'VCT': 'VC',
   'VEN': 'VE',
   'VGB': 'VG',
   'VIR': 'VI',
   'VNM': 'VN',
   'VUT': 'VU',
   'WLF': 'WF',
   'WSM': 'WS',
   'XKV': 'XK',
   'YEM': 'YE',
   'ZAF': 'ZA',
   'ZMB': 'ZM',
   'ZWE': 'ZW'}

  >>> print(alpha2to3.get('CH'))
  CHE

  >>> print(alpha3to2.get('CHE'))
  CH

  >>> print(alpha3to2.get(alpha2to3.get('CH')))
  CH

  >>> print(alpha2to3.get(alpha3to2.get('CHE')))
  CHE


MessageFactory
--------------

The package provides an own message factory using the iso3166 doamin:

  >>> from p01.vocabulary.country.i18n import MessageFactory as _iso3166_
  >>> _iso3166_
  <zope.i18nmessageid.message.MessageFactory object at ...>

  >>> text = _iso3166_('Switzerland')
  >>> print(text)
  Switzerland

  >>> text.domain
  'iso3166'

The translations given from the debian iso files are available. Let's register
the german and french catalog and an iso3166 translation domain:

  >>> import os
  >>> import zope.i18n
  >>> import zope.i18n.interfaces
  >>> import zope.i18n.translationdomain
  >>> import zope.i18n.gettextmessagecatalog
  >>> domain = zope.i18n.translationdomain.TranslationDomain('iso3166')
  >>> dePath = os.path.join(os.path.dirname(p01.vocabulary.country.__file__),
  ...     'locales', 'de', 'LC_MESSAGES', 'iso3166.mo')
  >>> frPath = os.path.join(os.path.dirname(p01.vocabulary.country.__file__),
  ...     'locales', 'fr', 'LC_MESSAGES', 'iso3166.mo')
  >>> catalog = zope.i18n.gettextmessagecatalog.GettextMessageCatalog('de',
  ...     'iso3166', dePath)
  >>> domain.addCatalog(catalog)
  >>> catalog = zope.i18n.gettextmessagecatalog.GettextMessageCatalog('fr',
  ...     'iso3166', frPath)
  >>> domain.addCatalog(catalog)
  >>> zope.component.provideUtility(domain,
  ...     zope.i18n.interfaces.ITranslationDomain, name='iso3166')

Now we can translate to german:

  >>> print(zope.i18n.translate(text, target_language='de'))
  Schweiz

or to french:

  >>> print(zope.i18n.translate(text, target_language='fr'))
  Suisse
