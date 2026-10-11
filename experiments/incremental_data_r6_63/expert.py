"""Explicit expert-selected actions, not observed AI tool trajectories or reasoning."""
def actions():
    # Independently written from frozen human-style source descriptions.
    choices = [
        ('D01','add',[{'ref':'arrivals'},{'ref':'reserve'}],'Int64',['arrivals','reserve']),
        ('D02','add',[{'const':1},{'ref':'count'}],'Int64',['count']),
        ('D03','add',[{'ref':'batch'},{'ref':'batch'}],'Int64',['batch']),
        ('D04','add',[{'ref':'subtotal'},{'ref':'adjustment'}],'Int64',['adjustment','subtotal']),
        ('D05','le',[{'ref':'load'},{'const':5}],'Bool',['load']),
        ('D06','le',[{'const':5},{'ref':'stock'}],'Bool',['stock']),
        ('D07','le',[{'ref':'requested'},{'ref':'available'}],'Bool',['available','requested']),
        ('D08','eq',[{'ref':'recorded'},{'ref':'reference'}],'Bool',['recorded','reference']),
        ('D09','eq',[{'ref':'first'},{'ref':'second'}],'Bool',['first','second']),
        ('D10','eq',[{'ref':'enabled'},{'const':True}],'Bool',['enabled'])]
    return {eid:dict(id='selected',type=typ,deps=deps,node=dict(op='value',expr={op:args}))
            for eid,op,args,typ,deps in choices}
