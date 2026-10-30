"""Installed contracts-only compatibility golden, identical before/after opt-in install."""
import hashlib
import json
import sys
from equity_feature_contracts import (ConfigSpec,Parameter,SessionSpec,IntervalSpec,WindowSpec,
    AvailabilitySpec,PriceUnit,builtin_registry)

def main():
    # Independent preexisting baseline d8ff...; literal schema envelope, no production serializer for expected bytes.
    expected={
        'identity':'synthetic:baseline','algorithm_version':'v1','schema_version':'1',
        'parameters':[{'name':'a','value':20},{'name':'z','value':{'float64':'0x1.8000000000000p+0'}}],
        'session':{'namespace':'demo','session_id':'S3','open_ns':100,'close_ns':200,'timezone_label':'caller-label',
            'intervals':[{'name':'opening','start_ns':100,'end_ns':120}],'scheduled_close_ns':None,
            'early_close':False,'include_opening_auction':False,'include_closing_auction':False},
        'window':{'count':2,'target_session_id':'S3','governed_sessions':['S1','S2','S3','S4'],'anchor':'prior_only'},
        'availability':{'market_cutoff_ns':200,'knowledge_cutoff_ns':210,'evaluation_ns':210,'mode':'known_at','reconstruction_reason':None},
        'adjustment':{'basis':'raw','policy_version':'raw-v1','action_snapshot':'none','anchor':'none'},
        'price_unit':{'scale':4,'currency':'USD'}}
    raw=json.dumps(expected,sort_keys=True,separators=(',',':'),ensure_ascii=True)
    assert hashlib.sha256(raw.encode()).hexdigest()=='d8ff9ddb56cf26be7e9550874f8891f4db5d3ee38ed3b6a7ac9a100a5fa9d8fc'
    c=ConfigSpec('synthetic:baseline','v1',(Parameter('z',1.5),Parameter('a',20)),
        SessionSpec('demo','S3',100,200,'caller-label',(IntervalSpec('opening',100,120),)),
        WindowSpec(2,'S3',('S1','S2','S3','S4')),AvailabilitySpec(200,210,210),price_unit=PriceUnit(4,'USD'))
    assert c.to_json()==raw;assert ConfigSpec.from_json(raw)==c
    assert c.digest=='d8ff9ddb56cf26be7e9550874f8891f4db5d3ee38ed3b6a7ac9a100a5fa9d8fc'
    assert len(builtin_registry().list_features())==40
    if '--continuous' in sys.argv:
        before=builtin_registry().list_features()
        from equity_feature_continuous import list_features
        assert len(list_features())==6
        assert builtin_registry().list_features()==before
    print('Legacy ConfigSpec1 golden d8ff9ddb/39IDs unchanged.')

if __name__=='__main__':main()
