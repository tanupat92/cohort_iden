<script>
  import { CSVDownloader } from 'svelte-csv';

  let data = []; 
  let summary_data = {};
  let query_result = {};
  let search_text = ""; 
  let limit = 10; 
  let type = 'all'; 
  let select_term = '';
  let select_desc = ''; 
  let query_text = ''; 

  const searchClick = async () => {
    let s = search_text.replace(/\s+/g, '+');
    const response = await fetch(`http://127.0.0.1:8000/search?terms=${s}&limit=${limit}&type=${type}`);
    data = await response.json();
    console.log(data);
    };
  
  const runClick = async () => {
    console.log(query_text);
    let q = query_text.trim()
    const response = await fetch(`http://127.0.0.1:8000/query?q=${q}`);
    query_result = await response.json();
    console.log(query_result);
    };

  async function onSelected(obj) {
    select_term = obj.concept_num;
    select_desc = obj.concept_term; 
    query_text += ` { ${select_term} | ${select_desc} } `;

    const response = await fetch(`http://127.0.0.1:8000/summary?id=${select_term}&type=lab`);
    summary_data = await response.json();
  }  
  function onLimitChange(event) {
		limit = event.currentTarget.value;
	}
  function onTypeChange(event) {
		type = event.currentTarget.value;
	}

</script>

<div>
  <h2>Cohort Identification</h2>
  <p>data: synthea</p>
  <p>how to use</p>
  <p>1. search a term</p>
  <p>2. identify constraints</p>
  <p>{" ie. ( { LOINC:39156-5 | Body mass index } > 40.0 ) and ( { LOINC:39156-5 | Body mass index } <= 45.0 )"}</p>
  <p>{" ( << { SNOMED:7063008 | Necrotizing pneumonia } ) "}</p>
  <p>{" ( { SNOMED:72892002 | Normal pregnancy (finding) } BEFORE  { SNOMED:44054006 | Diabetes mellitus type 2 (disorder) } ) "}</p>
</div>

<div>
  <input type="text" bind:value={search_text}>
  <button on:click={searchClick}>search</button>
</div>

<div>
  <label>
    <input type=radio name="limit" on:change={onLimitChange} checked={limit===10} value="10" />
    10
  </label>
  
  <label>
    <input type=radio name="limit" on:change={onLimitChange} checked={limit===20} value="20" />
    20
  </label>
  
  <label>
    <input type=radio name="limit" on:change={onLimitChange} checked={limit===50} value="50" />
    50
  </label>
</div>

<div>
  <label>
    <input type=radio name="type" on:change={onTypeChange} checked={type==="all"} value="all" />
    All
  </label>
  
  <label>
    <input type=radio name="type" on:change={onTypeChange} checked={type==="snomed"} value="snomed" />
    SNOMED only
  </label>
  
  <label>
    <input type=radio name="type" on:change={onTypeChange} checked={type==="loinc"} value="loinc" />
    Lab only
  </label>
</div>
<!-- <p>
  {JSON.stringify({data}, null, 2)}
</p> -->
<!-- <h1>{limit}</h1> -->
<div>
  {#if data.length > 0}
    {#each data as term}
      <button on:click={onSelected(term)} >{term.concept_term}</button>  
    {/each} 
  {/if}
</div>

<div>
  <h3>{select_term}</h3>
</div>

<div>
  {#if summary_data?.value }
    {#if summary_data.type === 'T'}
      <p>possible values: {summary_data.unit}</p>
    {:else}
        <p>possible units: {summary_data.unit}</p>
        <p>min: {summary_data?.value?.min}, max: {summary_data?.value?.max}, mean: {summary_data?.value?.mean}</p>
    {/if}
  {/if}
</div>


<div>
  <textarea bind:value={query_text} id="query_text" name="querytext" rows="8" cols="75" />
</div>
<button on:click={runClick}>Run</button>

<div>
  {#if Object.keys(query_result).length !== 0}

    <p>patient list : {JSON.stringify(query_result.patient_set)}</p>

    <CSVDownloader
      data={query_result.patient_set.map( (x) => { return {'patient_num': x}})}
      type={'button'}
      filename={'patient_set'}
      bom={true}
    >
      Download
    </CSVDownloader>
    <p>encounter list : {JSON.stringify(query_result.encounter_set)}</p>
    <CSVDownloader
      data={query_result.encounter_set.map( (x) => { return {'encounter_num': x}})}
      type={'button'}
      filename={'encounter_set'}
      bom={true}
    >
      Download
    </CSVDownloader>
  {/if}
</div>




<!-- ( { LOINC:39156-5 | Body mass index } > 40.0 ) and ( { LOINC:39156-5 | Body mass index } <= 45.0 ) -->

<!-- ( << { SNOMED:7063008 | Necrotizing pneumonia } ) -->

