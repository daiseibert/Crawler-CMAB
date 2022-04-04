# Crawler-CMAB

In the file: main.py. There is an example of greedy context guided crawler.
The idea in construct this context guided crawler is to understand what could be used in a CMAB in this situation.
The greedy context guided crawler is divided in sub-parts:
    - Defined a term, we search it on Wikipedia and the budget;
    - Check the size of the web page;
    - Get all the links;
    - Check the embeddings for each link;
    - Clean the embeddings (Is not found embeddings for each link term, if it is not found, discard it.)
    - Get the cosine similarity for each term compared with defined term.
    - Always Get the most similar to the defined term.
    - Calculated the action loss
    - Do this until budget allows.


- Embeddings: 
    - Not all words are in the used embedding method.
    - First is checked if there is an embedding for the word, if not check is there is an embedding for an entity.
        - For example, "bmw" (word) and "Bmw" (entity), both were found in this method. However, the embedding are not the same, so the first option was to use word, and if only found word embedding, could use the entity embedding.

- Possible improvements:
    - Check a better embedding method.
    - Use an elaborated loss function.
    - An idea that can be done is defined a term and departing by this term arrive in other specific term. With this idea is easy to define a loss and reward function, always trying to reach the term with minimum steps (clicking links).