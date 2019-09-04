import pytest
import requests
import time

from oi_sud.core.parser import CommonParser

#
@pytest.mark.skip
def test_requests(capsys):

    urls = ['http://gvs.adg.sudrf.ru', 'http://gvs.bkr.sudrf.ru', 'http://kyahinskygvs.bur.sudrf.ru',
            'http://ulanudegvs.bur.sudrf.ru', 'http://mgvs.dag.sudrf.ru', 'http://nalchikskygvs.kbr.sudrf.ru',
            'http://petrozavodskygvs.kar.sudrf.ru', 'http://gvs.komi.sudrf.ru', 'http://gvs.jak.sudrf.ru',
            'http://gvs.wlk.sudrf.ru', 'http://kazanskygvs.tat.sudrf.ru', 'http://gvs.hak.sudrf.ru',
            'http://bgvs.alt.sudrf.ru', 'http://ngvs.krd.sudrf.ru', 'http://gvs.krd.sudrf.ru',
            'http://sgvs.krd.sudrf.ru', 'http://kgvs.krk.sudrf.ru', 'http://vgvs.prm.sudrf.ru',
            'http://ugvs.prm.sudrf.ru', 'http://fgvs.prm.sudrf.ru', 'http://sdgvs.prm.sudrf.ru',
            'http://sgvs.stv.sudrf.ru', 'http://pgvs.stv.sudrf.ru', 'http://bgvs.stv.sudrf.ru',
            'http://krasnorechgvs.hbr.sudrf.ru', 'http://habargvs.hbr.sudrf.ru', 'http://knagvs.hbr.sudrf.ru',
            'http://s-gavanskygvs.hbr.sudrf.ru', 'http://sgvs.amr.sudrf.ru', 'http://bgvs.amr.sudrf.ru',
            'http://belgvs.amr.sudrf.ru', 'http://agvs.arh.sudrf.ru', 'http://vmgvs.arh.sudrf.ru',
            'http://sgvs.arh.sudrf.ru', 'http://astrahanskygvs.ast.sudrf.ru', 'http://znamenskygvs.ast.sudrf.ru',
            'http://gvs.brj.sudrf.ru', 'http://gvs.wld.sudrf.ru', 'http://95gvs.wld.sudrf.ru',
            'http://vgvs.vol.sudrf.ru', 'http://vologodskygvs.vld.sudrf.ru', 'http://gvs.vrn.sudrf.ru',
            'http://gvs.iwn.sudrf.ru', 'http://cheremhovskygvs.irk.sudrf.ru', 'http://irkutskygvs.irk.sudrf.ru',
            'http://kaliningvs.kln.sudrf.ru', 'http://baltyiskygvs.kln.sudrf.ru', 'http://kgvs.klg.sudrf.ru',
            'http://35gvs.kam.sudrf.ru', 'http://gvs.krs.sudrf.ru', 'http://vgvs.lo.sudrf.ru',
            'http://ogvs.mo.sudrf.ru', 'http://nfgvs.mo.sudrf.ru', 'http://sgvs.mo.sudrf.ru', 'http://bgvs.mo.sudrf.ru',
            'http://rgvs.mo.sudrf.ru', 'http://kgvs.mo.sudrf.ru', 'http://polgvs.mrm.sudrf.ru',
            'http://sevgvs.mrm.sudrf.ru', 'http://zaogvs.mrm.sudrf.ru', 'http://murmgvs.mrm.sudrf.ru',
            'http://gadjgvs.mrm.sudrf.ru', 'http://nizegorodskygvs.nnov.sudrf.ru', 'http://gvs.nvg.sudrf.ru',
            'http://gvs.nsk.sudrf.ru', 'http://ogvs.oms.sudrf.ru', 'http://61gvs.oms.sudrf.ru',
            'http://orenburgskygvs.orb.sudrf.ru', 'http://101gvs.orb.sudrf.ru', 'http://gvs.pnz.sudrf.ru',
            'http://voen.perm.sudrf.ru', 'http://gvs.psk.sudrf.ru', 'http://gvs.ros.sudrf.ru',
            'http://novocherkasskygvs.ros.sudrf.ru', 'http://rgvs.riz.sudrf.ru', 'http://gvs.sam.sudrf.ru',
            'http://saratovgvs.sar.sudrf.ru', 'http://yusgvs.sah.sudrf.ru', 'http://kgvs.sah.sudrf.ru',
            'http://egvs.svd.sudrf.ru', 'http://ntagvs.svd.sudrf.ru', 'http://sgvs.sml.sudrf.ru',
            'http://tgvs.tmb.sudrf.ru', 'http://tverskoy.twr.sudrf.ru', 'http://tomskygvs.tms.sudrf.ru',
            'http://gvs.tula.sudrf.ru', 'http://gvs.uln.sudrf.ru', 'http://mgvs.chel.sudrf.ru',
            'http://chgvs.chel.sudrf.ru', 'http://gvs.cht.sudrf.ru', 'http://gvsborza.cht.sudrf.ru',
            'http://yargvs.jrs.sudrf.ru', 'http://224gvs.spb.sudrf.ru', 'http://gvs.spb.sudrf.ru',
            'http://bgvs.brb.sudrf.ru', 'http://gvs.krm.sudrf.ru', 'http://gvs.chao.sudrf.ru',
            'http://gvs.sev.sudrf.ru', 'http://109gvs.svd.sudrf.ru', 'http://26gvs.kaz.sudrf.ru',
            'http://40gvs.blg.sudrf.ru', 'http://80gvs.msk.sudrf.ru', 'http://gvs.skav.sudrf.ru',
            'http://gvs.chn.sudrf.ru']

    c = CommonParser()

    bstart_time = time.time()
    c.send_get_requests(urls)
    print("--- %s seconds ---" % (time.time() - bstart_time))

    nstart_time = time.time()
    for u in urls:
        r, s = c.send_get_request(u)
        #print(s)
    print("--- %s seconds ---" % (time.time() - nstart_time))
    assert False
