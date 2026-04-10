# tests/conftest.py
import matplotlib
matplotlib.use('Agg')  # must be first

import io
import time
import pytest
import pandas as pd
import sys
import os

# Set test mode BEFORE importing pipeline
os.environ["TEST_MODE"] = "true"

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pipeline import ConversationMemory

# ── Rate limit delay between tests ───────────────────────────────
@pytest.fixture(autouse=True)
def rate_limit_delay():
    yield
    time.sleep(4)  # 4 sec between tests

# ── Sample CSV ────────────────────────────────────────────────────
SAMPLE_CSV = """Row ID,Order ID,Order Date,Ship Date,Ship Mode,Customer ID,Customer Name,Segment,Country,City,State,Postal Code,Region,Product ID,Category,Sub-Category,Product Name,Sales
1,CA-2017-152156,08/11/2017,11/11/2017,Second Class,CG-12520,Claire Gute,Consumer,United States,Henderson,Kentucky,42420,South,FUR-BO-10001798,Furniture,Bookcases,Bush Somerset Collection Bookcase,261.96
2,CA-2017-152156,08/11/2017,11/11/2017,Second Class,CG-12520,Claire Gute,Consumer,United States,Henderson,Kentucky,42420,South,FUR-CH-10000454,Furniture,Chairs,Hon Deluxe Fabric Upholstered Stacking Chairs,731.94
3,CA-2017-138688,12/06/2017,16/06/2017,Second Class,DV-13045,Darrin Van Huff,Corporate,United States,Los Angeles,California,90036,West,OFF-LA-10000240,Office Supplies,Labels,Self-Adhesive Address Labels,14.62
4,US-2016-108966,11/10/2016,18/10/2016,Standard Class,SO-20335,Sean O Donnell,Consumer,United States,Fort Lauderdale,Florida,33311,South,FUR-TA-10000577,Furniture,Tables,Bretford CR4500 Series Table,957.58
5,US-2016-108966,11/10/2016,18/10/2016,Standard Class,SO-20335,Sean O Donnell,Consumer,United States,Fort Lauderdale,Florida,33311,South,OFF-ST-10000760,Office Supplies,Storage,Eldon Fold N Roll Cart System,22.37
6,CA-2015-115812,09/06/2015,14/06/2015,Standard Class,BH-11710,Brosina Hoffman,Consumer,United States,Los Angeles,California,90032,West,FUR-FU-10001487,Furniture,Furnishings,Eldon Expressions Desk,48.86
7,CA-2015-115812,09/06/2015,14/06/2015,Standard Class,BH-11710,Brosina Hoffman,Consumer,United States,Los Angeles,California,90032,West,OFF-AR-10002833,Office Supplies,Art,Newell 322,7.28
8,CA-2015-115812,09/06/2015,14/06/2015,Standard Class,BH-11710,Brosina Hoffman,Consumer,United States,Los Angeles,California,90032,West,TEC-PH-10002275,Technology,Phones,Mitel 5320 IP Phone,907.15
9,CA-2015-115812,09/06/2015,14/06/2015,Standard Class,BH-11710,Brosina Hoffman,Consumer,United States,Los Angeles,California,90032,West,OFF-BI-10003910,Office Supplies,Binders,DXL Angle-View Binders,18.50
10,CA-2015-115812,09/06/2015,14/06/2015,Standard Class,BH-11710,Brosina Hoffman,Consumer,United States,Los Angeles,California,90032,West,OFF-AP-10002892,Office Supplies,Appliances,Belkin F5C206VTEL,114.90
11,CA-2014-161389,11/12/2014,13/12/2014,Second Class,LS-17230,Lena Cacioppo,Consumer,United States,Houston,Texas,77095,Central,OFF-BI-10004410,Office Supplies,Binders,Avery 5 inch binders,38.94
12,CA-2016-107727,15/04/2016,20/04/2016,Standard Class,BF-11020,Barry French,Consumer,United States,Philadelphia,Pennsylvania,19140,East,OFF-EN-10003985,Office Supplies,Envelopes,Poly String Tie Envelopes,16.45
13,CA-2016-107727,15/04/2016,20/04/2016,Standard Class,BF-11020,Barry French,Consumer,United States,Philadelphia,Pennsylvania,19140,East,OFF-AR-10004834,Office Supplies,Art,Faber-Castell ART GRIP,9.47
14,CA-2016-107727,15/04/2016,20/04/2016,Standard Class,BF-11020,Barry French,Consumer,United States,Philadelphia,Pennsylvania,19140,East,TEC-PH-10004977,Technology,Phones,Konftel 250 Conference phone,68.02
15,CA-2017-167164,13/09/2017,17/09/2017,Second Class,CS-12280,Clay Cheatham,Consumer,United States,Denver,Colorado,80219,West,OFF-BI-10001359,Office Supplies,Binders,Avery Durable Slant Ring Binders,15.55
16,CA-2017-143567,08/03/2017,10/03/2017,First Class,SC-20770,Sean Chen,Corporate,United States,Detroit,Michigan,48205,Central,OFF-ST-10004186,Office Supplies,Storage,Stur-D-Stor Shelving,13.98
17,CA-2017-143567,08/03/2017,10/03/2017,First Class,SC-20770,Sean Chen,Corporate,United States,Detroit,Michigan,48205,Central,OFF-BI-10003656,Office Supplies,Binders,Avery 508,4.97
18,CA-2014-134915,24/09/2014,29/09/2014,Second Class,CG-12505,Carlos Gomez,Consumer,United States,Philadelphia,Pennsylvania,19143,East,TEC-PH-10004945,Technology,Phones,Nikon Coolpix S570,523.58
19,CA-2014-134915,24/09/2014,29/09/2014,Second Class,CG-12505,Carlos Gomez,Consumer,United States,Philadelphia,Pennsylvania,19143,East,OFF-BI-10000756,Office Supplies,Binders,Wilson Jones Legal File Folders,11.78
20,CA-2014-134915,24/09/2014,29/09/2014,Second Class,CG-12505,Carlos Gomez,Consumer,United States,Philadelphia,Pennsylvania,19143,East,OFF-BI-10002215,Office Supplies,Binders,Acco 4 Button Clip,6.98
"""

@pytest.fixture(scope="session")
def sample_df():
    df = pd.read_csv(io.StringIO(SAMPLE_CSV))
    return df

@pytest.fixture(scope="function")
def fresh_memory():
    return ConversationMemory(max_turns=5)

@pytest.fixture(scope="session")
def real_df():
    real_path = os.path.join(os.path.dirname(__file__), "train.csv")
    if os.path.exists(real_path):
        return pd.read_csv(real_path)
    return pd.read_csv(io.StringIO(SAMPLE_CSV))