"""Matched-success accounting; no causal allocation of token differences to reuse."""
from common import OUT,load,save

def main():
    m=load(OUT/'MEASUREMENTS.json'); runs=m['runs']; development=m['totals']['DISCOVERY']
    discovery_tokens=development['tokens']['processed_input']+development['tokens']['output']
    contrasts={}
    for control in ['A','B','X']:
        rows=[]
        for task in ['E1','E2']:
            a,b=runs[task+'-'+control],runs[task+'-C']
            assert a['final_passed'] and b['final_passed']
            rows.append(dict(task=task,correct_both=True,successful_compact_references=1,
                processed_input_saved=a['tokens']['processed_input']-b['tokens']['processed_input'],
                output_saved=a['tokens']['output']-b['tokens']['output'],
                reported_processed_plus_output_saved=(a['tokens']['processed_input']+a['tokens']['output'])-
                    (b['tokens']['processed_input']+b['tokens']['output']),
                wall_saved=a['participant_wall_seconds']-b['participant_wall_seconds'],
                exact_retrieval_tokens=None))
        gross=sum(r['reported_processed_plus_output_saved'] for r in rows)
        contrasts[control]=dict(rows=rows,matched_success_gross_tokens_saved=gross,
            discovery_charged_net_tokens_saved=gross-discovery_tokens,
            average_observed_session_difference_per_reuse=gross/2,
            observed_token_break_even=None,positive_aggregate_reuse_saving=False,
            causal_tokens_saved_by_abstraction=None)
    save(OUT/'MATCHED-SUCCESS-AMORTIZATION.json',dict(contrasts=contrasts,
        no_demonstrated_net_economy=True,discovery_tokens=discovery_tokens,
        earlier_aggregate_B_21_reuses_is_illustrative_not_established=True,
        explanation='AMORTIZATION.json aggregates all tasks, including failed combination tasks and a B budget stop, then divides by two full successful reused references. Its arithmetic21 is not a measured per-reuse saving or an economic break-even estimate. Direct-transfer matched-success sessions have negative aggregate savings against every control.',
        API_billing=None,full_coordinator_and_library_freeze_effort=None))
    print(contrasts)

if __name__=='__main__': main()
