<script setup lang="ts">
import { askIAPrompt } from '@/fetchers/PriceData.ia.ftc';
import { watch } from 'vue';

const props = defineProps(["curdata", "companyname"]);

watch(() => props.companyname, () => {
    reset();
})

function reset(){
    const promptbox = (document.querySelector("#promptbox") as any);
    const ansbox = (document.querySelector("#ansbox") as any);

    promptbox.value = "";
    ansbox.innerHTML = "";
}

function sendPrompt(){
    const sendFinancial = (document.querySelector("#sendFinancialData") as any).checked;
    const promptbox = (document.querySelector("#promptbox") as any);
    const prompt = promptbox.value;
    const ansbox = (document.querySelector("#ansbox") as any);
    promptbox.value = "";
    ansbox.innerHTML += prompt;
    ansbox.innerHTML += "<br/>";
    if(prompt === ""){
        return
    }
    askIAPrompt(props.companyname, sendFinancial ? props.curdata : [], prompt).then((xAnswer) => {
            ansbox.innerHTML += "CRW : " + xAnswer.data.response;
            ansbox.innerHTML += "<br/>";
        })
        .catch((xReject) => {
        });
}
</script>

<template>
    <div id="tbox" class="row flex flex-col">
        <div class="ans-box grow" id="ansbox"></div>
        <div class="row max-h-16 w-full mt-3 self-end flex">
            <textarea id="promptbox" class="max-h-16 prompt-box" style="width: 80%;"></textarea>
            <input type="checkbox" name="isSendData" id="sendFinancialData"><span class="ml-2">Include Financial data ?</span></input>
            <button style="width: 20%;" @click="sendPrompt()" class="prompt-send">SEND</button>
        </div>
    </div>
</template>
<style>
#tbox{
    background-color: rgb(20, 20, 20);
    padding: 5px;
    
}

.ans-box{

}

.prompt-box{
    background-color: rgb(44, 44, 44);
}

.prompt-send{
    transition: all ease-in-out .2s;
    cursor: pointer;
}
.prompt-send:hover{
    background-color: rgb(47, 48, 49);
}
</style>
