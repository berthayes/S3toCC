import tempfile
import json
from configparser import ConfigParser

connect_conf = "connect.properties"
spooldir_conf_template = "csv_spooldir_config_template.json"
spooldir_generated_config = "csv_spooldir_config.json"

with tempfile.NamedTemporaryFile(delete=False, mode='wt') as t:
    t.write('[conf]')
    path = t.name
    #print(path)

    with open(connect_conf, 'r') as f:
        for line in f:
            t.write(line)


cfg = ConfigParser()
cfg.read(path)

schema_url = cfg.get('conf', 'value.converter.schema.registry.url')
schema_creds = cfg.get('conf', 'value.converter.schema.registry.basic.auth.user.info')
#print(schema_url)

with open(spooldir_conf_template, 'r') as f:
    spooldir_dict = json.loads(f.read())


config_dict = spooldir_dict['config']
config_dict['value.converter.schema.registry.url'] = schema_url
config_dict['key.converter.schema.registry.url'] = schema_url
config_dict['value.converter.schema.registry.basic.auth.user.info'] = schema_creds

#print(json.dumps(spooldir_dict))

with open(spooldir_generated_config, 'wt') as c:
    c.write(json.dumps(spooldir_dict, indent=4))
