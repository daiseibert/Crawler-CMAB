# Crawler-CMAB

In the file: main.py. There is a example of greedy context guided crawler.
The idea in cinstruct this context guided crawler is understand what could be used a CMAB in this situation.
The greedy context guided crawler is divided in sub-parts:
    - Defined a term we search it on Wikipedia and the budget;
    - Check the size of the web page;
    - Get all the links;
    - Check the embbedings for each link;
    - Clean the embbedings (Is not found embbedings for each link term, if it is not found, discart it.)
    - Get the cossine similarity for each term compared with defined term.
    - Get always the most similar to the defined term.
    - Calculated the action loss
    - Do this until budget allows.


- Embbedings: 
    - Not all words are in the used embbeding method.
    - First is checked if there is an embbeding for the word, if not check if there is a embbeding for an entity.
        - For example, "bmw" (word) and "Bmw" (entity), both were find. However the embbeding are not the same, so the first option was to use word, and if only found word embbeding, could use the entity embbeding.

- Possible improvements:
    - Check a better embbeding method.
    - Use an elaborated loss function.
    - An idea that can be done is define a term and departing by this term arrive in other specific term. With this idea is easy to define a loss and reward function, always trying to reach the term with minimum steps (clicking links).
