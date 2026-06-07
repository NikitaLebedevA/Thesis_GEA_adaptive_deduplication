function [p xij]=CreateXij(p, model)
    xij=zeros(model.I, model.J);

    for j=1:numel(p)
        xij(p(j), j)=1;
    end
end